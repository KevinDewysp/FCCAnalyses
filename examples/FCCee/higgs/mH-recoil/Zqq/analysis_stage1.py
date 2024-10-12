'''
Analysis example, measure Higgs mass in the Z(mumu)H recoil measurement.
'''
import os, copy
from argparse import ArgumentParser

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
jet_p_max = '110'

# Mandatory: Analysis class where the user defines the operations on the
# dataframe.
class Analysis():
    '''
    Higgs mass recoil analysis in Z(qq)H.
    '''
    def __init__(self, cmdline_args):
        parser = ArgumentParser(
            description='Additional analysis arguments',
            usage='Provide additional arguments after analysis script path')
        parser.add_argument('--muon-pt', default='10.', type=float,
                            help='Minimal pT of the mouns.')
        # Parse additional arguments not known to the FCCAnalyses parsers
        # All command line arguments know to fccanalysis are provided in the
        # `cmdline_arg` dictionary.
        self.ana_args, _ = parser.parse_known_args(cmdline_args['unknown'])

        # Mandatory: List of processes to run over
        self.process_list = {
            # Run the full statistics in one output file named
            # <outputDir>/p8_ee_ZZ_ecm240.root
            'p8_ee_ZZ_ecm240': {'fraction': 0.005},
            # Run the full statistics in one output file named
            # <outputDir>/p8_ee_Zqq_ecm240.root
            'p8_ee_Zqq_ecm240': {'fraction': 0.005},
            # Run 50% of the statistics with output into two files named
            # <outputDir>/p8_ee_WW_ecm240/chunk<N>.root
            'p8_ee_WW_ecm240': {'fraction': 0.0005},
            # Run 20% of the statistics in one file named
            # <outputDir>/p8_ee_ZH_ecm240_out.root (example on how to change
            # the output name)
            'wzp6_ee_qqH_ecm240': {'fraction': 0.0005,
                                'output': 'wzp6_ee_qqH_ecm240_out'}
        }

        # Mandatory: Production tag when running over the centrally produced
        # samples, this points to the yaml files for getting sample statistics
        self.prod_tag = "FCCee/winter2023/IDEA/"

        # Optional: output directory, default is local running directory
        self.output_dir = "/eos/user/k/kdewyspe/4_Sept/FCCee/MidTerm/Zqq/" \
                          f'stage1_{self.ana_args.muon_pt}'

        # Optional: analysisName, default is ''
        # self.analysis_name = 'My Analysis'

        # Optional: number of threads to run on, default is 'all available'
        # self.n_threads = 4

        # Optional: running on HTCondor, default is False
        # self.run_batch = False

        # Optional: test file
        self.test_file = 'root://eospublic.cern.ch//eos/experiment/fcc/ee/' \
                         'generation/DelphesEvents/winter2023/IDEA/' \
                         'p8_ee_ZH_ecm240/events_101027117.root'

    # Mandatory: analyzers function to define the analysis graph, please make
    # sure you return the dataframe, in this example it is dframe2
    def analyzers(self, dframe):
        '''
        Analysis graph.
        '''
        
        ## perform N=2 jet clustering
        global jetClusteringHelper
        global jetFlavourHelper

        # njets = 4 #5,6
        # tag = ''
        # collections = {
        #     "GenParticles": "Particle",
        #     "PFParticles": "ReconstructedParticles",
        #     "PFTracks": "EFlowTrack",
        #     "PFPhotons": "EFlowPhoton",
        #     "PFNeutralHadrons": "EFlowNeutralHadron",
        #     "TrackState": "EFlowTrack_1",
        #     "TrackerHits": "TrackerHits",
        #     "CalorimeterHits": "CalorimeterHits",
        #     "dNdx": "EFlowTrack_2",
        #     "PathLength": "EFlowTrack_L",
        #     "Bz": "magFieldBz",
        # }

        # ## define jet clustering parameters
        # jetClusteringHelper = ExclusiveJetClusteringHelper(
        #     collections["PFParticles"], njets, tag
        # )

        # df = jetClusteringHelper.define(df)

        # #muon_pt = self.ana_args.muon_pt

        # ## define jet flavour tagging parameters

        # jetFlavourHelper = JetFlavourHelper(
        #     collections,
        #     jetClusteringHelper.jets,
        #     jetClusteringHelper.constituents,
        #     tag,
        # )

        # ## define observables for tagger
        # df = jetFlavourHelper.define(df)

        # ## tagger inference
        # df = jetFlavourHelper.inference(weaver_preproc, weaver_model, df)

        dframe2 = (
            dframe
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

               .Define("FCCAnalysesJets_ee_genkt", "JetClustering::clustering_ee_genkt(0.5, 0, 0, 0, 0, 1)(pseudo_jets)")
               #get the jets out of the struct
               .Define("jets_ee_genkt",           "JetClusteringUtils::get_pseudoJets(FCCAnalysesJets_ee_genkt)")
               #get the jets constituents out of the struct
               .Define("jetconstituents_ee_genkt","JetClusteringUtils::get_constituents(FCCAnalysesJets_ee_genkt)")
               

               .Define(
                'selected_jets',
                'JetClusteringUtils::sel_p(' + jet_p_min + ',' + jet_p_max + ')(jets_ee_genkt)', # ' + jet_p_min + ',' + jet_p_max + ' 
                )
               .Define("n_jets",    "return selected_jets.size()")
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

               .Define("jets_ee_genkt_m_1",        "jets_ee_genkt_m[0]")
               .Define("jets_ee_genkt_m_2",        "jets_ee_genkt_m[1]")
               .Define("jets_ee_genkt_m_3",        "jets_ee_genkt_m[2]")
               .Define("jets_ee_genkt_m_4",        "jets_ee_genkt_m[3]")
               .Define("jets_ee_genkt_m_5",        "jets_ee_genkt_m[4]")
               .Define("jets_ee_genkt_m_6",        "jets_ee_genkt_m[5]")
        

            .Define(
                    'Z_hadronic',
                    'ReconstructedParticle::jetResonanceBuilder(91.2)(selected_jets)',
                )
            .Define(
                    'Z_hadronic_m', 'ReconstructedParticle::get_mass(Z_hadronic)' #[0]
                )
            .Define(
                    'Z_hadronic_p', 'ReconstructedParticle::get_p(Z_hadronic)'#[0]
                )
                # z->two jets, no p cut
                # .Define('Z_hadronic_2', 'ReconstructedParticle::multijetResonanceBuilder(91.2)(jets)')
            .Define(
                    'Z_hadronic_2',
                    'ReconstructedParticle::jetResonanceBuilder(91.2,1)(jets_ee_genkt)',
                )
            .Define(
                    'Z_hadronic_m_2',
                    'ReconstructedParticle::get_mass(Z_hadronic_2)',#[0]
                )
            .Define(
                    'Z_hadronic_p_2',
                    'ReconstructedParticle::get_p(Z_hadronic_2)',#[0]
                )
            .Define(
                    'higgs_hadronic',
                    'ReconstructedParticle::jetResonanceBuilder(125)(selected_jets)',
                )
            .Define(
                    'higgs_hadronic_m', 'ReconstructedParticle::get_mass(higgs_hadronic)'#[0]
                )
            .Define(
                    'higgs_hadronic_p', 'ReconstructedParticle::get_p(higgs_hadronic)'#[0]
                )
                # H->two jets, no p cut
                # .Define('higgs_hadronic_2', 'ReconstructedParticle::multijetResonanceBuilder(125)(jets)')
            .Define(
                    'higgs_hadronic_2',
                    'ReconstructedParticle::jetResonanceBuilder(125,1)(jets_ee_genkt)',
                )
            .Define(
                    'higgs_hadronic_m_2',
                    'ReconstructedParticle::get_mass(higgs_hadronic_2)',#[0]
                )
            .Define(
                    'higgs_hadronic_p_2',
                    'ReconstructedParticle::get_p(higgs_hadronic_2)',#[0]
                )
            
            # calculate recoil of the Z
            .Define(
                'zed_hadronic_recoil',
                'ReconstructedParticle::recoilBuilder(240)(Z_hadronic)',
            )
            .Define(
                'zed_hadronic_recoil_m',
                'ReconstructedParticle::get_mass(zed_hadronic_recoil)',#[0]
            )

            .Define(
                'zed_hadronic_recoil_2',
                'ReconstructedParticle::recoilBuilder(240)(Z_hadronic_2)',
            )
            .Define(
                'zed_hadronic_recoil_m_2',
                'ReconstructedParticle::get_mass(zed_hadronic_recoil_2)',#[0]
            )

        #     .Define(
        #     "missingEnergy",
        #     "FCCAnalyses::ZHfunctions::missingEnergy(240., ReconstructedParticles)",
        #     )

            # .Define("cosTheta_miss", "FCCAnalyses::get_cosTheta_miss(missingEnergy)")
        #     .Define(
        #     "cosTheta_miss",
        #     "FCCAnalyses::ZHfunctions::get_cosTheta_miss(MissingET)",
        #     )

            .Define(
            "missing_p",
            "FCCAnalyses::ReconstructedParticle::get_p(MissingET)",
            )

            # Filter at least one candidate
            .Filter('zed_hadronic_recoil_m.size()>0')
        )

       
        

        return dframe2

    # Mandatory: output function, please make sure you return the branch list
    # as a python list
    def output(self):
        '''
        Output variables which will be saved to output root file.
        '''
        branch_list = [
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

        #     'jet_flavour',
        #     'jet_flavour_1',
        #     'jet_flavour_2',
        #     'jet_flavour_3',
        #     'jet_flavour_4',
        #     'jet_flavour_5',
        #     'jet_flavour_6',

            'Z_hadronic',

            # "jets_ee_genkt",
            # "jetconstituents_ee_genkt",

            # recoil mass
            'zed_hadronic_recoil_m',
            'zed_hadronic_recoil_m_2',

        #     "missingEnergy",
        #     "cosTheta_miss",
            "missing_p",

            "n_jets",

        ]
        return branch_list
