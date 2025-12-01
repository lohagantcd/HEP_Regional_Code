#ifndef __NCP_PRINT_MACROS__
#define __NCP_PRINT_MACROS__

//
//  printAll          - Print array of data names, values, units, IOstatus and description
//  printData         - Print array of data names and values
//  printDependents   - Print only solver dependent names and values
//  printDescription  - Print array of data names, values and description
//  printIndependents - Print only solver independent names and values
//  printIOstatus     - Print array of data names, values and IOstatus
//  printPride        - Print solver Indep and Dep names and values
//  printUnit         - Print array of data names, values and units
//  printValue        - Calls printData
//

// ***********************
//
//  printAll
//
// ***********************
void printAll(string Names[]){
  int i;
  for (i=0; i<Names.entries(); i+=1) {
    cout << Names[i] << " = " << Names[i]->value
         << " (" << Names[i]->units << ") {" 
	 << Names[i]->IOstatus << "}" << endl
	 << "(description: " << Names[i]->description << " )\n" << endl;
  }
  cout << endl;
}

// ***********************
//
//  printData
//
// ***********************
void printData(string Names[]) {
  int i;
  for (i=0; i<Names.entries(); i+=1) {
    cout << Names[i] << " = " << Names[i]->value << endl;
  }
  cout << endl;
}

// ***********************
//
//  printDependents
//
// ***********************
void printDependents() {
  int i;
  string Names[];
  string templ, tempr;
  Names = solver.list("Dependent",1);
  cout << endl << " Name_lhs = Value  |  Name_rhs = Value (Solver Dependents)" << endl;
  for (i=0; i<Names.entries(); i+=1) {
    templ = Names[i]->eq_lhs;
    tempr = Names[i]->eq_rhs;
    if (tempr == "0.0000") {
      cout << templ << " = " << templ->value << "  |  " << tempr << endl;
    }
    else {
      cout << templ << " = " << templ->value << "  |  " << tempr << " = " << tempr->value << endl;
    }
  }
  cout << endl;
}

// ***********************
//
//  printDescription
//
// ***********************
void printDescription(string Names[]){
  int i;
  for (i=0; i<Names.entries(); i+=1) {
    cout << Names[i] << " = " << Names[i]->value
	 << "(description: " << Names[i]->description << " )\n" << endl;
  }
  cout << endl;
}

// ***********************
//
//  printIndependents
//
// ***********************
void printIndependents() {
  int i;
  string Names[];
  string temp;
  Names = solver.list("Independent",1);
  cout << endl << " Name = Value (Solver Independents)" << endl;
  for (i=0; i<Names.entries(); i+=1) {
    temp = Names[i]->varName;
    cout << temp << " = " << temp->value << endl;
  }
  cout << endl;
}

// ***********************
//
//  printIOstatus
//
// ***********************
void printIOstatus(string Names[]) {
  int i;
  for (i=0; i<Names.entries(); i+=1) {
    cout << Names[i] << " = " << Names[i]->value << " (" << Names[i]->IOstatus << ")" << endl;
  }
  cout << endl;
}

// ***********************
//
//  printPride
//
// ***********************
void printPride(){
  int i, j;
  real DeplVal, DeprVal, IndVal;
  string Ind;
  string Depl;
  string Depr;
  string NamDep[];
  string NamInd[];
  NamDep=solver.list("Dependent",1);
  NamInd=solver.list("Independent",1);
  cout << "\n\n" << "  Solver Pride " << endl 
       << endl << " Indep Name = Value  |  Dep_lhs Name = Value  |  Dep_rhs Name = Value"
       << endl << " ------------------     --------------------     --------------------"
       << endl;
  for (i=0; i<NamInd.entries(); i+=1) {
    j = i + 1;
    Ind  = NamInd[i]->varName;
    if(NamInd[i]->getName() != NamInd[i]) {
      Ind = NamInd[i]->getPathName() + "." + Ind;
    }
    Depl = NamDep[i]->eq_lhs;
    Depr = NamDep[i]->eq_rhs;
    if (.exists(Ind)) {
        IndVal = Ind->value;
      }
    else {
        IndVal = NamInd[i]->x;
    }
    if (.exists(Depl)) {
        DeplVal = Depl->value;
      }
    else {
        DeplVal = NamDep[i]->y1;
    }
    if (.exists(Depr)) {
        DeprVal = Depr->value;
      }
    else {
        DeprVal = NamDep[i]->y2;
    }
    cout << " " << j << ") "
         << Ind  << " = " << IndVal  << "  |  " 
         << Depl << " = " << DeplVal << "  |  " 
         << Depr << " = " << DeprVal << endl;
  }
  cout << endl;
  cout << " Solver Statistics \n"
       << " ------------------------------\n"
       << " solutionMode = " << solver.solutionMode << ","
       << " converged = " << solver.converged << endl
       << " iterationCounter = " << solver.iterationCounter << ","
       << " passCounter = " << solver.passCounter << endl
       << " numJacobians = " << solver.numJacobians << ","
       << " numBroydens = " << solver.numBroydens << "\n\n";
}

// ***********************
//
//  printUnits
//
// ***********************
void printUnits(string Names[]) {
  int i;
  for (i=0; i<Names.entries(); i+=1) {
    cout << Names[i] << " = " << Names[i]->value << " (" << Names[i]->units << ")" << endl;
  }
  cout << endl;
}

// ***********************
//
//  printValue
//
// ***********************
void printValue(string Names[]){
  printData(Names);
}


#endif
