ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> findZleptons(const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& legs) {

  int Zdau1(-1), Zdau2(-1);
  float Zmass(1e9);
  int n = legs.size();
  //ROOT::VecOps::RVec<bool> result(n);
  //std::fill(result.begin(), result.end(), false);
  ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData> result;

  if (n>1) {
    ROOT::VecOps::RVec<bool> v(n);
    std::fill(v.end() - 2, v.end(), true);
    do {
      edm4hep::ReconstructedParticleData reso;
      TLorentzVector reso_lv;
      float m1(-999.), m2(-999.);
      int i1(-1), i2(-1);
      for (int i = 0; i < n; ++i) {
        if (v[i]) {
          reso.charge += legs[i].charge;
          TLorentzVector leg_lv;
          leg_lv.SetXYZM(legs[i].momentum.x, legs[i].momentum.y, legs[i].momentum.z, legs[i].mass);
          reso_lv += leg_lv;
          
          if (m1<0) {
            m1 = legs[i].mass;
            i1 = i;
          }
          else {
            m2 = legs[i].mass;
            i2 = i;
          }
        }
      }
      // CONSIDER ONLY OPPOSITE CHARGE SAME FLAVOUR COMBINATIONS
      // debug
      //std::cout << i1 << " " << i2 << std:: endl;
      //std::cout << reso.charge << std:: endl;
      //std::cout << m1-m2 << std:: endl;
      if (reso.charge==0 && std::abs(m1-m2)<1e-5) {
        reso.momentum.x = reso_lv.Px();
        reso.momentum.y = reso_lv.Py();
        reso.momentum.z = reso_lv.Pz();
        reso.mass = reso_lv.M();
        // debug
        //std::cout << reso.mass << std::endl;
        if (abs(reso.mass - 91.2)<abs(Zmass - 91.2)) {
          Zmass = reso.mass;
          Zdau1 = i1;
          Zdau2 = i2;
        }
      }
    } while (std::next_permutation(v.begin(), v.end()));
  }
  if (Zdau1>-1 and Zdau2>-1) {
    // debug
    // std::cout << "Selected pair: " << Zdau1 << " " << Zdau2 << ", mass: " << Zmass << std::endl;
    //result[Zdau1] = true;
    //result[Zdau2] = true;
    result.push_back(legs[Zdau1]);
    result.push_back(legs[Zdau2]);
  }
  return result;
}