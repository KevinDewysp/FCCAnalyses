import os, copy

# list of processes
processList = {
    # Signal
    'wzp6_ee_qqH_ecm240': {'fraction': 0.01 ,'chunks': 1, },
    # Background
    # 'p8_ee_ZZ_ecm240': {'chunks': 80},
    # 'p8_ee_WW_ecm240': {'chunks': 80},
    # 'p8_ee_Zqq_ecm240': {'chunks': 80},
}

# Production tag when running over EDM4Hep centrally produced events, this points to the yaml files for getting sample statistics (mandatory)
prodTag     = "FCCee/winter2023/IDEA/"

#Optional: output directory, default is local running directory
outputDir= "/eos/user/k/kdewyspe/4_Sept/FCCee/MidTerm/Zqq_240/MVAInputs_test_n7/"

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
jet_p_max = '100'


# Mandatory: RDFanalysis class where the use defines the operations on the TTree
class RDFanalysis:

    # __________________________________________________________
    # Mandatory: analysers funtion to define the analysers to process, please make sure you return the last dataframe, in this example it is df2
    def analysers(df):

        # # __________________________________________________________
        # # Mandatory: analysers funtion to define the analysers to process, please make sure you return the last dataframe, in this example it is df2

        # # define some aliases to be used later on
        # df = df.Alias("Particle0", "Particle#0.index")
        # df = df.Alias("Particle1", "Particle#1.index")
        # df = df.Alias("MCRecoAssociations0", "MCRecoAssociations#0.index")
        # df = df.Alias("MCRecoAssociations1", "MCRecoAssociations#1.index")
        # df = df.Alias("Muon0", "Muon#0.index")
        # # get all the leptons from the collection
        # df = df.Define(
        #     "muons_all",
        #     "FCCAnalyses::ReconstructedParticle::get(Muon0, ReconstructedParticles)",
        # )
        # # select leptons with momentum > 20 GeV
        # df = df.Define(
        #     "muons",
        #     "FCCAnalyses::ReconstructedParticle::sel_p(20)(muons_all)",
        # )
        # df = df.Define(
        #     "muons_p", "FCCAnalyses::ReconstructedParticle::get_p(muons)"
        # )
        # df = df.Define(
        #     "muons_theta",
        #     "FCCAnalyses::ReconstructedParticle::get_theta(muons)",
        # )
        # df = df.Define(
        #     "muons_phi",
        #     "FCCAnalyses::ReconstructedParticle::get_phi(muons)",
        # )
        # df = df.Define(
        #     "muons_q",
        #     "FCCAnalyses::ReconstructedParticle::get_charge(muons)",
        # )
        # df = df.Define(
        #     "muons_no", "FCCAnalyses::ReconstructedParticle::get_n(muons)"
        # )
        # # compute the muon isolation and store muons with an isolation cut of 0df = df.25 in a separate column muons_sel_iso
        # df = df.Define(
        #     "muons_iso",
        #     "FCCAnalyses::ZHfunctions::coneIsolation(0.01, 0.5)(muons, ReconstructedParticles)",
        # )
        # df = df.Define(
        #     "muons_sel_iso",
        #     "FCCAnalyses::ZHfunctions::sel_iso(0.25)(muons, muons_iso)",
        # )

        # #########
        # ### CUT 1: at least 1 muon with at least one isolated one
        # #########
        # df = df.Filter("muons_no >= 1 && muons_sel_iso.size() > 0")
        # #########
        # ### CUT 2 :at least 2 opposite-sign (OS) leptons
        # #########
        # df = df.Filter("muons_no >= 2 && abs(Sum(muons_q)) < muons_q.size()")
        # now we build the Z resonance based on the available leptons.
        # the function resonanceBuilder_mass_recoil returns the best lepton pair compatible with the Z mass (91.2 GeV) and recoil at 125 GeV
        # the argument 0.4 gives a weight to the Z mass and the recoil mass in the chi2 minimization
        # technically, it returns a ReconstructedParticleData object with index 0 the di-lepton system, index and 2 the leptons of the pair

        ## here cluster jets in the events but first remove muons from the list of
        ## reconstructed particles

        ## create a new collection of reconstructed particles removing muons with p>20
        # df = df.Define(
        #     "ReconstructedParticlesNoMuons",
        #     "FCCAnalyses::ReconstructedParticle::remove(ReconstructedParticles,muons)",
        # )

        ## perform N=2 jet clustering
        global jetClusteringHelper
        global jetFlavourHelper

        ## define jet and run clustering parameters
        ## name of collections in EDM root files
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



        # # define jet clustering parameters
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

        # df = df.Define('event_d23', 'JetClusteringUtils::get_exclusive_dmerge(_jet, 2)')
        # df = df.Define('event_d34', 'JetClusteringUtils::get_exclusive_dmerge(_jet, 3)')
        # df = df.Define('event_d45', 'JetClusteringUtils::get_exclusive_dmerge(_jet, 4)')
        
        df = df.Define(
                'jet_flavour', 'JetTaggingUtils::get_flavour(jet, Particle)' #, 2, 0.8
            )
        df = (df.Define(
                'selected_jets',
                'JetClusteringUtils::sel_p(' + jet_p_min + ',' + jet_p_max + ')(jet)', # ' + jet_p_min + ',' + jet_p_max + '
            )
        .Define('n_selected_jets', 'JetClusteringUtils::get_n(selected_jets)')
        .Define('selected_jets_pt', 'JetClusteringUtils::get_pt(selected_jets)')
        .Define('selected_jets_eta', 'JetClusteringUtils::get_eta(selected_jets)')
        .Define('selected_jets_p', 'JetClusteringUtils::get_p(selected_jets)')
        .Define('selected_jets_m', 'JetClusteringUtils::get_m(selected_jets)')

        .Define('selected_jet1_pt', 'selected_jets_pt[0]')
        .Define('selected_jet2_pt', 'selected_jets_pt[1]')
        .Define('selected_jet3_pt', 'selected_jets_pt[2]')
        .Define('selected_jet4_pt', 'selected_jets_pt[3]')

        .Define('selected_jet1_eta', 'selected_jets_eta[0]')
        .Define('selected_jet2_eta', 'selected_jets_eta[1]')
        .Define('selected_jet3_eta', 'selected_jets_eta[2]')
        .Define('selected_jet4_eta', 'selected_jets_eta[3]')

        .Define('selected_jet1_p', 'selected_jets_p[0]')
        .Define('selected_jet2_p', 'selected_jets_p[1]')
        .Define('selected_jet3_p', 'selected_jets_p[2]')
        .Define('selected_jet4_p', 'selected_jets_p[3]')

        .Define('selected_jet1_m', 'selected_jets_m[0]')
        .Define('selected_jet2_m', 'selected_jets_m[1]')
        .Define('selected_jet3_m', 'selected_jets_m[2]')
        .Define('selected_jet4_m', 'selected_jets_m[3]')
        )
        # df = df.Define("m_jj", "JetConstituentsUtils::InvariantMass(selected_jets_tlv[0], selected_jets_tlv[1])")

        # df = df.Define(
        #     "zbuilder_result",
        #     "FCCAnalyses::ZHfunctions::resonanceBuilder_mass_recoil(91.2, 125, 0.4, 240, false)(jets_p4, MCRecoAssociations0, MCRecoAssociations1, ReconstructedParticles, Particle, jets_p4[0], jets_p4[1])",
        # )
        # df = df.Define("zmumu", "Vec_rp{zbuilder_result[0]}")  # the Z
        # df = df.Define(
        #     "zmumu_muons", "Vec_rp{zbuilder_result[1],zbuilder_result[2]}"
        # )  # the leptons
        # df = df.Define(
        #     "zmumu_m",
        #     "FCCAnalyses::ReconstructedParticle::get_mass(zmumu)[0]",
        # )  # Z mass
        # df = df.Define(
        #     "zmumu_p", "FCCAnalyses::ReconstructedParticle::get_p(zmumu)[0]"
        # )  # momentum of the Z
        # df = df.Define(
        #     "zmumu_recoil",
        #     "FCCAnalyses::ReconstructedParticle::recoilBuilder(240)(zmumu)",
        # )  # compute the recoil based on the reconstructed Z
        # df = df.Define(
        #     "zmumu_recoil_m",
        #     "FCCAnalyses::ReconstructedParticle::get_mass(zmumu_recoil)[0]",
        # )  # recoil mass
        # df = df.Define(
        #     "zmumu_muons_p",
        #     "FCCAnalyses::ReconstructedParticle::get_p(zmumu_muons)",
        # )  # get the momentum of the 2 muons from the Z resonance

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

        # #########
        # ### CUT 3: Njets = 2
        # #########
        # df = df.Filter("event_njet > 1")

        # df = df.Define(
        #     "jets_p4",
        #     "JetConstituentsUtils::compute_tlv_jets({})".format(
        #         jetClusteringHelper.jets
        #     ),
        # )
        # df = df.Define(
        #     "jj_m",
        #     "JetConstituentsUtils::InvariantMass(jets_p4[0], jets_p4[1])",
        # )

        df = (df.Define(
                'Z_hadronic',
                'ReconstructedParticle::jetResonanceBuilder(91.2)(selected_jets)',
            )
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
                'ReconstructedParticle::jetResonanceBuilder(91.2,1)(jet)',
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
                'ReconstructedParticle::jetResonanceBuilder(125,1)(jet)',
            )
        .Define(
                'higgs_hadronic_m_2',
                'ReconstructedParticle::get_mass(higgs_hadronic_2)[0]',
            )
        .Define(
                'higgs_hadronic_p_2',
                'ReconstructedParticle::get_p(higgs_hadronic_2)[0]',
            )
        )

        df = (
            df.Define('jet1_E', 'jet_e[0]')
            .Define('jet2_E', 'jet_e[1]')
            .Define('jet3_E', 'jet_e[2]')
            .Define('jet4_E', 'jet_e[3]')

            .Define('jet1_nconst', 'jet_nconst[0]')
            .Define('jet2_nconst', 'jet_nconst[1]')
            .Define('jet3_nconst', 'jet_nconst[2]')
            .Define('jet4_nconst', 'jet_nconst[3]')

            # .Define('jet1_isB', 'recojet_isB[0]')
            # .Define('jet2_isB', 'recojet_isB[1]')
            # .Define('jet3_isB', 'recojet_isB[2]')
            # .Define('jet4_isB', 'recojet_isB[3]')

            # .Define('jet1_isC', 'recojet_isC[0]')
            # .Define('jet2_isC', 'recojet_isC[1]')
            # .Define('jet3_isC', 'recojet_isC[2]')
            # .Define('jet4_isC', 'recojet_isC[3]')

            # .Define('jet1_isS', 'recojet_isS[0]')
            # .Define('jet2_isS', 'recojet_isS[1]')
            # .Define('jet3_isS', 'recojet_isS[2]')
            # .Define('jet4_isS', 'recojet_isS[3]')

            # .Define('jet1_isQ', 'recojet_isQ[0]')
            # .Define('jet2_isQ', 'recojet_isQ[1]')
            # .Define('jet3_isQ', 'recojet_isQ[2]')
            # .Define('jet4_isQ', 'recojet_isQ[3]')

            # .Define('jet1_isU', 'recojet_isU[0]')
            # .Define('jet2_isU', 'recojet_isU[1]')
            # .Define('jet3_isU', 'recojet_isU[2]')
            # .Define('jet4_isU', 'recojet_isU[3]')

            # .Define('jet1_isD', 'recojet_isD[0]')
            # .Define('jet2_isD', 'recojet_isD[1]')
            # .Define('jet3_isD', 'recojet_isD[2]')
            # .Define('jet4_isD', 'recojet_isD[3]')

            # .Define('jet1_isTAU', 'recojet_isTAU[0]')
            # .Define('jet2_isTAU', 'recojet_isTAU[1]')
            # .Define('jet3_isTAU', 'recojet_isTAU[2]')
            # .Define('jet4_isTAU', 'recojet_isTAU[3]')

            # .Define('jet1_isG', 'recojet_isG[0]')
            # .Define('jet2_isG', 'recojet_isG[1]')
            # .Define('jet3_isG', 'recojet_isG[2]')
            # .Define('jet4_isG', 'recojet_isG[3]')
        )
        

        return df

    # __________________________________________________________
    # Mandatory: output function, please make sure you return the branchlist as a python list
    def output():
        branchList = [
            # "zmumu_m",
            # "zmumu_p",
            # "zmumu_recoil_m",
            "cosTheta_miss",
            "missing_p",
            # "m_jj",
        ]

        ##  outputs jet properties
        # branchList += jetClusteringHelper.outputBranches()

        ## outputs jet scores and constituent breakdown
        branchList += jetFlavourHelper.outputBranches()
        branchList += [
            # 'event_d23',
            # 'event_d34',
            # 'event_d45',
            'jet_flavour',
            'jet1_E',
            'jet2_E',
            'jet3_E',
            'jet4_E',
            'jet1_nconst',
            'jet2_nconst',
            'jet3_nconst',
            'jet4_nconst',
            # 'selected_jets',
            # 'jet1_isB',
            # 'jet2_isB',
            # 'jet3_isB',
            # 'jet4_isB',
            # 'jet1_isC',
            # 'jet2_isC',
            # 'jet3_isC',
            # 'jet4_isC',
            # 'jet1_isS',
            # 'jet2_isS',
            # 'jet3_isS',
            # 'jet4_isS',
            # 'jet1_isQ',
            # 'jet2_isQ',
            # 'jet3_isQ',
            # 'jet4_isQ',
            # 'jet1_isU',
            # 'jet2_isU',
            # 'jet3_isU',
            # 'jet4_isU',
            # 'jet1_isD',
            # 'jet2_isD',
            # 'jet3_isD',
            # 'jet4_isD',
            # 'jet1_isTAU',
            # 'jet2_isTAU',
            # 'jet3_isTAU',
            # 'jet4_isTAU',
            # 'jet1_isG',
            # 'jet2_isG',
            # 'jet3_isG',
            # 'jet4_isG',
            'n_selected_jets',
            'selected_jets_p',
            'selected_jets_pt',
            'selected_jets_eta',
            'selected_jets_m',

            'selected_jet1_p',
            'selected_jet2_p',
            'selected_jet3_p',
            'selected_jet4_p',

            'selected_jet1_eta',
            'selected_jet2_eta',
            'selected_jet3_eta',
            'selected_jet4_eta',

            'selected_jet1_m',
            'selected_jet2_m',
            'selected_jet3_m',
            'selected_jet4_m',

            'selected_jet1_pt',
            'selected_jet2_pt',
            'selected_jet3_pt',
            'selected_jet4_pt',

            'Z_hadronic_m',
            'Z_hadronic_p',
            'Z_hadronic_m_2',
            'Z_hadronic_p_2',
            'higgs_hadronic_m',
            'higgs_hadronic_p',
            'higgs_hadronic_m_2',
            'higgs_hadronic_p_2',
            # 'etmiss',
        ]
        return branchList
