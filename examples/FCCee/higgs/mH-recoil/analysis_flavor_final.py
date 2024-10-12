'''
Final stage of the example Z(qq)H recoil mass analysis.
'''

# Define the input dir (optional)
inputDir    = "/eos/user/k/kdewyspe/4_Sept/FCCee/MidTerm/Zqq_240/MVAInputs_kt_flav_4/"

# Optional: output directory, default is local running directory
outputDir = "/eos/user/k/kdewyspe/4_Sept/FCCee/MidTerm/Zqq_240/MVAInputs_kt_flav_4/final_1/"


processList = {
    # Signal
    'wzp6_ee_qqH_ecm240': {'fraction': 0.1 ,'chunks': 1, },
    # Background
    'p8_ee_ZZ_ecm240': {'fraction': 0.001 ,'chunks': 1, },
    'p8_ee_WW_ecm240': {'fraction': 0.001 ,'chunks': 1,},
    'p8_ee_Zqq_ecm240': {'fraction': 0.001 ,'chunks': 1,},
}

# Link to the dictionary that contains all the cross section information etc...
procDict = "FCCee_procDict_winter2023_IDEA.json"

# Add MySample_p8_ee_ZH_ecm240 as it is not an offical process
# procDictAdd = {"MySample_p8_ee_ZH_ecm240": {"numberOfEvents": 10000000,
#                                             "sumOfWeights": 10000000,
#                                             "crossSection": 0.201868,
#                                             "kfactor": 1.0,
#                                             "matchingEfficiency": 1.0}}

# Expected integrated luminosity
intLumi = 10800000  # 10.8 /ab

# Whether to scale to expected integrated luminosity
doScale = True

# Number of threads to use
nCPUS = -1

# Whether to produce ROOT TTrees, default is False
doTree = True

# Save cut yields and efficiencies in LaTeX table
saveTabular = True

# Save cut yields and efficiencies in JSON file
saveJSON = True

# Dictionary with the list of cuts. The key is the name of the selection that
# will be added to the output file
cutList = {"sel0": "",
           "sel1_Z": "Z_hadronic_m > 86 && Z_hadronic_m < 96",
           "sel2_Recoil": "zed_hadronic_recoil_m < 160 && zed_hadronic_recoil_m > 100",
           "sel3_All": "Z_hadronic_m > 86 && Z_hadronic_m < 96 && zed_hadronic_recoil_m < 160 && zed_hadronic_recoil_m > 100" 
          }


# Dictionary for the output variables/histograms. The key is the name of the
# variable in the output files. "name" is the name of the variable in the input
# file, "title" is the x-axis label of the histogram, "bin" the number of bins
# of the histogram, "xmin" the minimum x-axis value and "xmax" the maximum
# x-axis value.
histoList = {
    "mz": {"name": "Z_hadronic_m",
           "title": "m_{Z} [GeV]",
           "bin": 125, "xmin": 0, "xmax": 250},
    "mz_zoom": {"name": "Z_hadronic_m",
                "title": "m_{Z} [GeV]",
                "bin": 40, "xmin": 80, "xmax": 100},
    "hadronic_recoil_m": {"name": "zed_hadronic_recoil_m",
                          "title": "Z hadronic recoil [GeV]",
                          "bin": 100, "xmin": 0, "xmax": 200},
    "hadronic_recoil_m_zoom": {"name": "zed_hadronic_recoil_m",
                               "title": "Z hadronic recoil [GeV]",
                               "bin": 200, "xmin": 80, "xmax": 160},
    "hadronic_recoil_m_zoom1": {"name": "zed_hadronic_recoil_m",
                                "title": "Z hadronic recoil [GeV]",
                                "bin": 100, "xmin": 120, "xmax": 140},
    "hadronic_recoil_m_zoom2": {"name": "zed_hadronic_recoil_m",
                                "title": "Z hadronic recoil [GeV]",
                                "bin": 200, "xmin": 120, "xmax": 140},
    "hadronic_recoil_m_zoom3": {"name": "zed_hadronic_recoil_m",
                                "title": "Z hadronic recoil [GeV]",
                                "bin": 400, "xmin": 120, "xmax": 140},
    "hadronic_recoil_m_zoom4": {"name": "zed_hadronic_recoil_m",
                                "title": "Z hadronic recoil [GeV]",
                                "bin": 800, "xmin": 120, "xmax": 140},
    "hadronic_recoil_m_zoom5": {"name": "zed_hadronic_recoil_m",
                                "title": "Z hadronic recoil [GeV]",
                                "bin": 2000, "xmin": 120, "xmax": 140},
    "hadronic_recoil_m_zoom6": {"name": "zed_hadronic_recoil_m",
                                "title": "Z hadronic recoil [GeV]",
                                "bin": 100, "xmin": 130.3, "xmax": 132.5},
    # # 1D histogram (alternative syntax)
    # "mz_1D": {"cols": ["Z_hadronic_m"],
    #           "title": "m_{Z} [GeV]",
    #           "bins": [(40, 80, 100)]},
    # # 2D histogram
    # "mz_recoil_2D": {"cols": ["Z_hadronic_m", "zed_hadronic_recoil_m"],
    #                  "title": "m_{Z} - hadronic recoil [GeV]",
    #                  "bins": [(40, 80, 100), (100, 120, 140)]},
    # # 3D histogram
    # "mz_recoil_3D": {
    #     "cols": ["Z_hadronic_m", "zed_hadronic_recoil_m", "zed_hadronic_recoil_m"],
    #     "title": "m_{Z} - hadronic recoil - hadronic recoil [GeV]",
    #     "bins": [(40, 80, 100), (100, 120, 140), (100, 120, 140)]},
}