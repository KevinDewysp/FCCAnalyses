import os, copy

# list of processes
processList = {
    # Signal
    'wzp6_ee_qqH_ecm240': {'fraction': 0.1 ,'chunks': 1, },
    'wzp6_ee_qqH_Htautau_ecm240': {'fraction': 0.1 ,'chunks': 1, },
    'wzp6_ee_qqH_Hss_ecm240': {'fraction': 0.1 ,'chunks': 1, },
    'wzp6_ee_qqH_HWW_ecm240': {'fraction': 0.1 ,'chunks': 1, },
    'wzp6_ee_qqH_Hgg_ecm240': {'fraction': 0.1 ,'chunks': 1, },
    'wzp6_ee_qqH_Hbb_ecm240': {'fraction': 0.1 ,'chunks': 1, },
    'wzp6_ee_qqH_Hcc_ecm240': {'fraction': 0.1 ,'chunks': 1, },
    'wzp6_ee_qqH_HZZ_ecm240': {'fraction': 0.1 ,'chunks': 1, },
    'wzp6_ee_qqH_Hmumu_ecm240': {'fraction': 0.1 ,'chunks': 1, },
    # # Background
    'p8_ee_ZZ_ecm240': {'fraction': 0.001 ,'chunks': 1,},
    'p8_ee_WW_ecm240': {'fraction': 0.001 ,'chunks': 1,},
    'p8_ee_Zqq_ecm240': {'fraction': 0.001 ,'chunks': 1,},
}

# Production tag when running over EDM4Hep centrally produced events, this points to the yaml files for getting sample statistics (mandatory)
prodTag     = "FCCee/winter2023/IDEA/"

#Optional: output directory, default is local running directory
outputDir= "/eos/user/k/kdewyspe/4_Sept/FCCee/MidTerm/Zqq_240/MVAInputs_R06_2/"

# Define the input dir (optional)
# inputDir    = "localSamples/"


# additional/costom C++ functions, defined in header files (optional)
includePaths = ["functions.h"]

## latest particle transformer model, trained on 9M jets in winter2023 samples
model_name = "fccee_flavtagging_edm4hep_wc_v1"

## model files needed for unit testing in CI
url_model_dir = "https://fccsw.web.cern.ch/fccsw/testsamples/jet_flavour_tagging/winter2023/wc_pt_13_01_2022/"
url_preproc = "{}/{}.json".format(url_model_dir, model_name)
url_model = "{}/{}.onnx".format(url_model_dir, model_name)

## model files locally stored on /eos
model_dir = (
    "/eos/experiment/fcc/ee/jet_flavour_tagging/winter2023/wc_pt_13_01_2022/"
)
local_preproc = "{}/{}.json".format(model_dir, model_name)
local_model = "{}/{}.onnx".format(model_dir, model_name)

## get local file, else download from url
def get_file_path(url, filename):
    if os.path.exists(filename):
        return os.path.abspath(filename)
    else:
        urllib.request.urlretrieve(url, os.path.basename(url))
        return os.path.basename(url)


weaver_preproc = get_file_path(url_preproc, local_preproc)
weaver_model = get_file_path(url_model, local_model)

from addons.ONNXRuntime.jetFlavourHelper import JetFlavourHelper
from addons.FastJet.jetClusteringHelper import (
    ExclusiveJetClusteringHelper,
)

jetFlavourHelper = None
jetClusteringHelper = None

jet_p_min = '15'
jet_p_max = '115'


# Mandatory: RDFanalysis class where the use defines the operations on the TTree
class RDFanalysis:

    # __________________________________________________________
    # Mandatory: analysers funtion to define the analysers to process, please make sure you return the last dataframe, in this example it is df2
    def analysers(df):
        
        ## perform N=2 jet clustering
        global jetClusteringHelper
        global jetFlavourHelper

        njets = 4 #5,6
        tag = ''
        collections = {
            "GenParticles": "Particle",
            "PFParticles": "ReconstructedParticles",
            "PFTracks": "EFlowTrack",
            "PFPhotons": "EFlowPhoton",
            "PFNeutralHadrons": "EFlowNeutralHadron",
            "TrackState": "EFlowTrack_1",
            "TrackerHits": "TrackerHits",
            "CalorimeterHits": "CalorimeterHits",
            "dNdx": "EFlowTrack_2",
            "PathLength": "EFlowTrack_L",
            "Bz": "magFieldBz",
        }

        ## define jet clustering parameters
        jetClusteringHelper = ExclusiveJetClusteringHelper(
            collections["PFParticles"], njets, tag
        )

        df = jetClusteringHelper.define(df)

        df = df.Define("jets_p4", "JetConstituentsUtils::compute_tlv_jets({})".format(jetClusteringHelper.jets))
        df = df.Define("m_jj", "JetConstituentsUtils::InvariantMass(jets_p4[0], jets_p4[1])")


        ## define jet flavour tagging parameters

        jetFlavourHelper = JetFlavourHelper(
            collections,
            jetClusteringHelper.jets,
            jetClusteringHelper.constituents,
            tag,
        )

        ## define observables for tagger
        df = jetFlavourHelper.define(df)

        ## tagger inference
        df = jetFlavourHelper.inference(weaver_preproc, weaver_model, df)

        df = (df
              
            #define the RP px, py, pz and e
               .Define("RP_px",          "ReconstructedParticle::get_px(ReconstructedParticles)")
               .Define("RP_py",          "ReconstructedParticle::get_py(ReconstructedParticles)")
               .Define("RP_pz",          "ReconstructedParticle::get_pz(ReconstructedParticles)")
               .Define("RP_pt",          "ReconstructedParticle::get_pt(ReconstructedParticles)")
               .Define("RP_p",           "ReconstructedParticle::get_p(ReconstructedParticles)")
               .Define("RP_e",           "ReconstructedParticle::get_e(ReconstructedParticles)")
               .Define("RP_m",           "ReconstructedParticle::get_mass(ReconstructedParticles)")
               .Define("RP_q",           "ReconstructedParticle::get_charge(ReconstructedParticles)")

               #build pseudo jets with the RP, using the interface that takes px,py,pz,m for better
               #handling of rounding errors
               .Define("pseudo_jets",    "JetClusteringUtils::set_pseudoJets_xyzm(RP_px, RP_py, RP_pz, RP_m)")

               .Define("FCCAnalysesJets_ee_genkt", "JetClustering::clustering_ee_genkt(0.6, 0, 0, 0, 0, 1)(pseudo_jets)")
               #get the jets out of the struct
               .Define("jets_ee_genkt",           "JetClusteringUtils::get_pseudoJets(FCCAnalysesJets_ee_genkt)")
               #get the jets constituents out of the struct
               .Define("jetconstituents_ee_genkt","JetClusteringUtils::get_constituents(FCCAnalysesJets_ee_genkt)")


               .Define('n_jets', 'JetClusteringUtils::get_n(jets_ee_genkt)')

               .Define(
                'selected_jets',
                'JetClusteringUtils::sel_p(' + jet_p_min + ',' + jet_p_max + ')(jets_ee_genkt)', # ' + jet_p_min + ',' + jet_p_max + ' 
                )
               .Define('n_selected_jets', 'JetClusteringUtils::get_n(selected_jets)')
            #    .Define("type_jets",     "selected_jets.type()")

               #get some variables
               .Define("jets_ee_genkt_px",        "JetClusteringUtils::get_px(selected_jets)")
               .Define("jets_ee_genkt_py",        "JetClusteringUtils::get_py(selected_jets)")
               .Define("jets_ee_genkt_pz",        "JetClusteringUtils::get_pz(selected_jets)")
               .Define("jets_ee_genkt_pt",        "JetClusteringUtils::get_pt(selected_jets)")
               .Define("jets_ee_genkt_p",        "JetClusteringUtils::get_p(selected_jets)")
               .Define("jets_ee_genkt_m",        "JetClusteringUtils::get_m(selected_jets)")  

               .Define("jets_ee_genkt_px_1",        "jets_ee_genkt_px[0]")
               .Define("jets_ee_genkt_px_2",        "jets_ee_genkt_px[1]")
               .Define("jets_ee_genkt_px_3",        "jets_ee_genkt_px[2]")
               .Define("jets_ee_genkt_px_4",        "jets_ee_genkt_px[3]")
               .Define("jets_ee_genkt_px_5",        "jets_ee_genkt_px[4]")
               .Define("jets_ee_genkt_px_6",        "jets_ee_genkt_px[5]")

               .Define("jets_ee_genkt_py_1",        "jets_ee_genkt_py[0]")
               .Define("jets_ee_genkt_py_2",        "jets_ee_genkt_py[1]")
               .Define("jets_ee_genkt_py_3",        "jets_ee_genkt_py[2]")
               .Define("jets_ee_genkt_py_4",        "jets_ee_genkt_py[3]")
               .Define("jets_ee_genkt_py_5",        "jets_ee_genkt_py[4]")
               .Define("jets_ee_genkt_py_6",        "jets_ee_genkt_py[5]")

               .Define("jets_ee_genkt_pz_1",        "jets_ee_genkt_pz[0]")
               .Define("jets_ee_genkt_pz_2",        "jets_ee_genkt_pz[1]")
               .Define("jets_ee_genkt_pz_3",        "jets_ee_genkt_pz[2]")
               .Define("jets_ee_genkt_pz_4",        "jets_ee_genkt_pz[3]")
               .Define("jets_ee_genkt_pz_5",        "jets_ee_genkt_pz[4]")
               .Define("jets_ee_genkt_pz_6",        "jets_ee_genkt_pz[5]")

               .Define("jets_ee_genkt_pt_1",        "jets_ee_genkt_pt[0]")
               .Define("jets_ee_genkt_pt_2",        "jets_ee_genkt_pt[1]")
               .Define("jets_ee_genkt_pt_3",        "jets_ee_genkt_pt[2]")
               .Define("jets_ee_genkt_pt_4",        "jets_ee_genkt_pt[3]")
               .Define("jets_ee_genkt_pt_5",        "jets_ee_genkt_pt[4]")
               .Define("jets_ee_genkt_pt_6",        "jets_ee_genkt_pt[5]")

               .Define("jets_ee_genkt_p_1",        "jets_ee_genkt_p[0]")
               .Define("jets_ee_genkt_p_2",        "jets_ee_genkt_p[1]")
               .Define("jets_ee_genkt_p_3",        "jets_ee_genkt_p[2]")
               .Define("jets_ee_genkt_p_4",        "jets_ee_genkt_p[3]")
               .Define("jets_ee_genkt_p_5",        "jets_ee_genkt_p[4]")
               .Define("jets_ee_genkt_p_6",        "jets_ee_genkt_p[5]")
               .Define("jets_ee_genkt_p_7",        "jets_ee_genkt_p[6]")
               .Define("jets_ee_genkt_p_8",        "jets_ee_genkt_p[7]")
               .Define("jets_ee_genkt_p_9",        "jets_ee_genkt_p[8]")
               .Define("jets_ee_genkt_p_10",        "jets_ee_genkt_p[9]")

               .Define("jets_ee_genkt_m_1",        "jets_ee_genkt_m[0]")
               .Define("jets_ee_genkt_m_2",        "jets_ee_genkt_m[1]")
               .Define("jets_ee_genkt_m_3",        "jets_ee_genkt_m[2]")
               .Define("jets_ee_genkt_m_4",        "jets_ee_genkt_m[3]")
               .Define("jets_ee_genkt_m_5",        "jets_ee_genkt_m[4]")
               .Define("jets_ee_genkt_m_6",        "jets_ee_genkt_m[5]")

        )

        df = (df
              
            .Define(
                    'Z_hadronic',
                    'ReconstructedParticle::jetResonanceBuilder(91.2)(selected_jets)',
                )
            .Define(
                    'Z_jets',
                    'ReconstructedParticle::findZjets(selected_jets)',
                )

            .Define(
                    'NonZ_jets',
                    'ReconstructedParticle::findZjets(selected_jets)',
                )
            
            .Define(
            'Zjets_flavour', 'JetTaggingUtils::get_flavour(Z_jets, Particle)' #, 2, 0.8
            )
            .Define(
            'Zjets_flavour_1', 'Zjets_flavour[0]' #, 2, 0.8
            )
              .Define(
            'Zjets_flavour_2', 'Zjets_flavour[1]' #, 2, 0.8
            )

            .Define("Z_jets_px",        "JetClusteringUtils::get_px(Z_jets)")
            .Define("Z_jets_py",        "JetClusteringUtils::get_py(Z_jets)")
            .Define("Z_jets_pz",        "JetClusteringUtils::get_pz(Z_jets)")
            .Define("Z_jets_pt",        "JetClusteringUtils::get_pt(Z_jets)")
            .Define("Z_jets_p",        "JetClusteringUtils::get_p(Z_jets)")
            .Define("Z_jets_m",        "JetClusteringUtils::get_m(Z_jets)") 

            .Define("Z_jets_px_1",        "Z_jets_px[0]")
            .Define("Z_jets_px_2",        "Z_jets_px[1]")
            .Define("Z_jets_px_3",        "Z_jets_px[2]")

            .Define("Z_jets_py_1",        "Z_jets_py[0]")
            .Define("Z_jets_py_2",        "Z_jets_py[1]")
            .Define("Z_jets_py_3",        "Z_jets_py[2]")

            .Define("Z_jets_pz_1",        "Z_jets_pz[0]")
            .Define("Z_jets_pz_2",        "Z_jets_pz[1]")
            .Define("Z_jets_pz_3",        "Z_jets_pz[2]")

            .Define("Z_jets_p_1",        "Z_jets_p[0]")
            .Define("Z_jets_p_2",        "Z_jets_p[1]")
            .Define("Z_jets_p_3",        "Z_jets_p[2]")

            .Define("Z_jets_pt_1",        "Z_jets_pt[0]")
            .Define("Z_jets_pt_2",        "Z_jets_pt[1]")
            .Define("Z_jets_pt_3",        "Z_jets_pt[2]")

            .Define("Z_jets_m_1",        "Z_jets_m[0]")
            .Define("Z_jets_m_2",        "Z_jets_m[1]")
            .Define("Z_jets_m_3",        "Z_jets_m[2]")

            .Define("NonZ_jets_px",        "JetClusteringUtils::get_px(NonZ_jets)")
            .Define("NonZ_jets_py",        "JetClusteringUtils::get_py(NonZ_jets)")
            .Define("NonZ_jets_pz",        "JetClusteringUtils::get_pz(NonZ_jets)")
            .Define("NonZ_jets_pt",        "JetClusteringUtils::get_pt(NonZ_jets)")
            .Define("NonZ_jets_p",        "JetClusteringUtils::get_p(NonZ_jets)")
            .Define("NonZ_jets_m",        "JetClusteringUtils::get_m(NonZ_jets)") 

            .Define("NonZ_jets_px_1",        "NonZ_jets_px[0]")
            .Define("NonZ_jets_px_2",        "NonZ_jets_px[1]")
            .Define("NonZ_jets_px_3",        "NonZ_jets_px[2]")
            .Define("NonZ_jets_px_4",        "NonZ_jets_px[3]")
            .Define("NonZ_jets_px_5",        "NonZ_jets_px[4]")
            .Define("NonZ_jets_px_6",        "NonZ_jets_px[5]")

            .Define("NonZ_jets_py_1",        "NonZ_jets_py[0]")
            .Define("NonZ_jets_py_2",        "NonZ_jets_py[1]")
            .Define("NonZ_jets_py_3",        "NonZ_jets_py[2]")

            .Define("NonZ_jets_pz_1",        "NonZ_jets_pz[0]")
            .Define("NonZ_jets_pz_2",        "NonZ_jets_pz[1]")
            .Define("NonZ_jets_pz_3",        "NonZ_jets_pz[2]")

            .Define("NonZ_jets_p_1",        "NonZ_jets_p[0]")
            .Define("NonZ_jets_p_2",        "NonZ_jets_p[1]")
            .Define("NonZ_jets_p_3",        "NonZ_jets_p[2]")

            .Define("NonZ_jets_pt_1",        "NonZ_jets_pt[0]")
            .Define("NonZ_jets_pt_2",        "NonZ_jets_pt[1]")
            .Define("NonZ_jets_pt_3",        "NonZ_jets_pt[2]")

            .Define("NonZ_jets_m_1",        "NonZ_jets_m[0]")
            .Define("NonZ_jets_m_2",        "NonZ_jets_m[1]")
            .Define("NonZ_jets_m_3",        "NonZ_jets_m[2]")

            # .Define('n_Zjets', 'return Z_jets.size()')
            # .Define('n_NonZjets', 'JetClusteringUtils::get_n(NonZ_jets)')

            .Define(
                    'Z_hadronic_m', 'ReconstructedParticle::get_mass(Z_hadronic)[0]'
                )
            .Define(
                    'Z_hadronic_p', 'ReconstructedParticle::get_p(Z_hadronic)[0]'
                )
                # z->two jets, no p cut
                # .Define('Z_hadronic_2', 'ReconstructedParticle::multijetResonanceBuilder(91.2)(jets)')
            .Define(
                    'Z_hadronic_2',
                    'ReconstructedParticle::jetResonanceBuilder(91.2,1)(jets_ee_genkt)',
                )
            .Define(
                    'Z_hadronic_m_2',
                    'ReconstructedParticle::get_mass(Z_hadronic_2)[0]', 
                )
            .Define(
                    'Z_hadronic_p_2',
                    'ReconstructedParticle::get_p(Z_hadronic_2)[0]',
                )
            .Define(
                    'higgs_hadronic',
                    'ReconstructedParticle::jetResonanceBuilder(125)(selected_jets)',
                )
            .Define(
                    'higgs_hadronic_m', 'ReconstructedParticle::get_mass(higgs_hadronic)[0]'
                )
            .Define(
                    'higgs_hadronic_p', 'ReconstructedParticle::get_p(higgs_hadronic)[0]'
                )
                # H->two jets, no p cut
                # .Define('higgs_hadronic_2', 'ReconstructedParticle::multijetResonanceBuilder(125)(jets)')
            .Define(
                    'higgs_hadronic_2',
                    'ReconstructedParticle::jetResonanceBuilder(125,1)(jets_ee_genkt)',
                )
            .Define(
                    'higgs_hadronic_m_2',
                    'ReconstructedParticle::get_mass(higgs_hadronic_2)[0]',
                )
            .Define(
                    'higgs_hadronic_p_2',
                    'ReconstructedParticle::get_p(higgs_hadronic_2)[0]',
                )
            
            # calculate recoil of the Z
            .Define(
                'zed_hadronic_recoil',
                'ReconstructedParticle::recoilBuilder(240)(Z_hadronic)',
            )
            .Define(
                'zed_hadronic_recoil_m',
                'ReconstructedParticle::get_mass(zed_hadronic_recoil)[0]',
            )

            .Define(
                'zed_hadronic_recoil_2',
                'ReconstructedParticle::recoilBuilder(240)(Z_hadronic_2)',
            )
            .Define(
                'zed_hadronic_recoil_m_2',
                'ReconstructedParticle::get_mass(zed_hadronic_recoil_2)[0]',
            )

            # .Define("jets_Z",           "JetClusteringUtils::get_pseudoJets(Z_hadronic)")

        )

        df = df.Define(
            "missingEnergy",
            "FCCAnalyses::ZHfunctions::missingEnergy(240., ReconstructedParticles)",
        )
        # .Define("cosTheta_miss", "FCCAnalyses::get_cosTheta_miss(missingEnergy)")
        df = df.Define(
            "cosTheta_miss",
            "FCCAnalyses::ZHfunctions::get_cosTheta_miss(MissingET)",
        )

        df = df.Define(
            "missing_p",
            "FCCAnalyses::ReconstructedParticle::get_p(MissingET)",
        )

        df = (df
              .Define(
            'jet_flavour', 'JetTaggingUtils::get_flavour(jets_ee_genkt, Particle)' #, 2, 0.8
            )

            .Define(
            'jet_flavour_sel', 'JetTaggingUtils::get_flavour(selected_jets, Particle)' #, 2, 0.8
            )
              .Define(
            'jet_flavour_1', 'jet_flavour[0]' #, 2, 0.8
            )
              .Define(
            'jet_flavour_2', 'jet_flavour[1]' #, 2, 0.8
            )
              .Define(
            'jet_flavour_3', 'jet_flavour[2]' #, 2, 0.8
            )
              .Define(
            'jet_flavour_4', 'jet_flavour[3]' #, 2, 0.8
            )
              .Define(
            'jet_flavour_5', 'jet_flavour[4]' #, 2, 0.8
            )
              .Define(
            'jet_flavour_6', 'jet_flavour[5]' #, 2, 0.8
            )

            .Define(
            'jet_flavour_sel_1', 'jet_flavour_sel[0]' #, 2, 0.8
            )

            #   .Define(
            # 'jet_IS_b', 'JetTaggingUtils::get_btag(Z_hadronic, 1)' #, 2, 0.8
            # )
            #   .Define(
            # 'jet_IS_c', 'JetTaggingUtils::get_ctag(Z_hadronic, 1)' #, 2, 0.8
            # )
            #   .Define(
            # 'jet_IS_l', 'JetTaggingUtils::get_ltag(Z_hadronic, 1)' #, 2, 0.8
            # )
        )

        return df

    # __________________________________________________________
    # Mandatory: output function, please make sure you return the branchlist as a python list
    def output():
        branchList = [
            "jets_ee_genkt_px",
            "jets_ee_genkt_py",
            "jets_ee_genkt_pz",
            "jetconstituents_ee_genkt",

            "jets_ee_genkt_px_1",
            "jets_ee_genkt_px_2",
            "jets_ee_genkt_px_3",
            "jets_ee_genkt_px_4",
            "jets_ee_genkt_px_5",
            "jets_ee_genkt_px_6",

            "jets_ee_genkt_py_1",
            "jets_ee_genkt_py_2",
            "jets_ee_genkt_py_3",
            "jets_ee_genkt_py_4",
            "jets_ee_genkt_py_5",
            "jets_ee_genkt_py_6",

            "jets_ee_genkt_pz_1",
            "jets_ee_genkt_pz_2",
            "jets_ee_genkt_pz_3",
            "jets_ee_genkt_pz_4",
            "jets_ee_genkt_pz_5",
            "jets_ee_genkt_pz_6",

            "jets_ee_genkt_p_1",
            "jets_ee_genkt_p_2",
            "jets_ee_genkt_p_3",
            "jets_ee_genkt_p_4",
            "jets_ee_genkt_p_5",
            "jets_ee_genkt_p_6",
            "jets_ee_genkt_p_7",
            "jets_ee_genkt_p_8",
            "jets_ee_genkt_p_9",
            "jets_ee_genkt_p_10",

            "jets_ee_genkt_pt_1",
            "jets_ee_genkt_pt_2",
            "jets_ee_genkt_pt_3",
            "jets_ee_genkt_pt_4",
            "jets_ee_genkt_pt_5",
            "jets_ee_genkt_pt_6",

            "jets_ee_genkt_m_1",
            "jets_ee_genkt_m_2",
            "jets_ee_genkt_m_3",
            "jets_ee_genkt_m_4",
            "jets_ee_genkt_m_5",
            "jets_ee_genkt_m_6",

            "jets_ee_genkt_m", 

            'Z_hadronic_m',
            'Z_hadronic_p',
            'Z_hadronic_m_2',
            'Z_hadronic_p_2',
            'higgs_hadronic_m',
            'higgs_hadronic_p',
            'higgs_hadronic_m_2',
            'higgs_hadronic_p_2',

            'jet_flavour',
            'jet_flavour_1',
            'jet_flavour_2',
            'jet_flavour_3',
            'jet_flavour_4',
            'jet_flavour_5',
            'jet_flavour_6',

            'Z_hadronic',

            # "jets_ee_genkt",
            # "jetconstituents_ee_genkt",

            # recoil mass
            'zed_hadronic_recoil_m',
            'zed_hadronic_recoil_m_2',

            "missingEnergy",
            "cosTheta_miss",
            "missing_p",

            "n_jets",
            "n_selected_jets",
            # "n_Zjets",
            # "n_NonZjets",

            "Z_jets_px_1", 
            "Z_jets_px_2", 
            "Z_jets_px_3", 

            "Z_jets_py_1", 
            "Z_jets_py_2", 
            "Z_jets_py_3", 

            "Z_jets_pz_1", 
            "Z_jets_pz_2", 
            "Z_jets_pz_3", 

            "Z_jets_p_1", 
            "Z_jets_p_2", 
            "Z_jets_p_3", 

            "Z_jets_pt_1", 
            "Z_jets_pt_2", 
            "Z_jets_pt_3", 

            "Z_jets_m_1", 
            "Z_jets_m_2", 
            "Z_jets_m_3", 

            "NonZ_jets_px_1", 
            "NonZ_jets_px_2", 
            "NonZ_jets_px_3", 
            "NonZ_jets_px_4", 
            "NonZ_jets_px_5", 
            "NonZ_jets_px_6",

            "NonZ_jets_py_1", 
            "NonZ_jets_py_2", 
            "NonZ_jets_py_3", 

            "NonZ_jets_pz_1", 
            "NonZ_jets_pz_2", 
            "NonZ_jets_pz_3", 

            "NonZ_jets_p_1", 
            "NonZ_jets_p_2", 
            "NonZ_jets_p_3", 

            "NonZ_jets_pt_1", 
            "NonZ_jets_pt_2", 
            "NonZ_jets_pt_3", 

            "NonZ_jets_m_1", 
            "NonZ_jets_m_2", 
            "NonZ_jets_m_3", 

            'Zjets_flavour_1', 
            'Zjets_flavour_2', 

            'jet_flavour_sel_1',

            # "jets_Z",

            # "RP_px",
            # "RP_py",
            # "RP_pz",
            # "RP_p",
            # "RP_pt",
            # "RP_m",
            # "RP_e",

            # "pseudo_jets", 

        ]

        ##  outputs jet properties
        # branchList += jetClusteringHelper.outputBranches()

        # ## outputs jet scores and constituent breakdown
        # branchList += jetFlavourHelper.outputBranches()
        # branchList += [
        #     # 'etmiss',
        #     # "jets_ee_genkt_px",
        #     # "jets_ee_genkt_py",
        #     # "jets_ee_genkt_pz",
        #     # "jetconstituents_ee_genkt",
        #     # 'jet_flavour',
        #     # 'jet_IS_b',
        #     # 'jet_IS_c',
        #     # 'jet_IS_l',
            

        # ]
        return branchList
