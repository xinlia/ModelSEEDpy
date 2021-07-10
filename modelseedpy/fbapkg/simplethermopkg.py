# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
from modelseedpy.fbapkg.basefbapkg import BaseFBAPkg
from modelseedpy.fbapkg.revbinpkg import RevBinPkg

#Base class for FBA packages
class SimpleThermoPkg(BaseFBAPkg):
    def __init__(self,model):
        BaseFBAPkg.__init__(self,model,"simple thermo",{"potential":"metabolite", "revbin":"reaction"},{"thermo":"reaction", "revbinF":"reaction", "revbinR":"reaction"})
        
    def validate_parameters(self):
        BaseFBAPkg.validate_parameters(self, self.parameters, [], {"filter":None, "min_potential":0, "max_potential":1000})
        
    def build_package(self,parameters):
        self.validate_parameters()
        #self.childpkgs["reversible binary"].build_package(self.parameters["filter"])
        for metabolite in self.model.metabolites:
            self.build_variable(metabolite)
        for reaction in self.model.reactions:
            #Checking that reaction passes input filter if one is provided
            if self.parameters["filter"] == None or reaction.id in self.parameters["filter"]:
                self.build_constraint(reaction)
    
    def build_variable(self,object):
        self.validate_parameters()
        return BaseFBAPkg.build_variable(self,"potential",self.parameters["min_potential"],self.parameters["max_potential"],"continuous",object)

    def build_constraint(self,object):#Gibbs: dg = Sum(st(i,j)*p(j))
        if object.id not in self.variables['revbin']:
            RevBinPkg.build_variable(self, object)
            RevBinPkg.build_constraint(self, object)
            
        #0 <= 1000*revbin(i) + Sum(st(i,j)*p(j)) <= 1000
        coef = {self.variables["revbin"][object.id] : 1000}
        for metabolite in object.metabolites:
            if metabolite.id not in self.variables['potential']:
                self.build_variable(metabolite)
            coef[self.variables["potential"][metabolite.id]] = object.metabolites[metabolite]
        return BaseFBAPkg.build_constraint(self,"thermo",0,1000,coef,object)