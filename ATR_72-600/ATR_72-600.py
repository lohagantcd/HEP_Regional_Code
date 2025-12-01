# tut_mission_B737.py
# 
# Created:  Aug 2014, SUAVE Team
# Modified: Aug 2017, SUAVE Team
#           Mar 2020, E. Botero

# ----------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------

# General Python Imports
import numpy as np
# Numpy is a commonly used mathematically computing package. It contains many frequently used
# mathematical functions and is faster than native Python, especially when using vectorized
# quantities.
import matplotlib.pyplot as plt
# Matplotlib's pyplot can be used to generate a large variety of plots. Here it is used to create
# visualizations of the aircraft's performance throughout the mission.

# SUAVE Imports
import SUAVE
assert SUAVE.__version__=='2.5.2', 'These tutorials only work with the SUAVE 2.5.2 release'
from SUAVE.Core import Data, Units, Container
# The Data import here is a native SUAVE data structure that functions similarly to a dictionary.
#   However, iteration directly returns values, and values can be retrieved either with the 
#   typical dictionary syntax of "entry['key']" or the more class-like "entry.key". For this to work
#   properly, all keys must be strings.
# The Units import is used to allow units to be specified in the vehicle setup (or elsewhere).
#   This is because SUAVE functions generally operate using metric units, so inputs must be 
#   converted. To use a length of 20 feet, set l = 20 * Units.ft . Additionally, to convert to SUAVE
#   output back to a desired units, use l_ft = l_m / Units.ft
from SUAVE.Methods.Geometry.Two_Dimensional.Planform import segment_properties
from SUAVE.Plots.Performance.Mission_Plots import *
from SUAVE.Plots.Geometry.plot_vehicle import *
from SUAVE.Plots.Geometry.plot_vehicle_vlm_panelization import *
from SUAVE.Components.Wings.Segment import Segment
from SUAVE.Methods.Propulsion.propeller_design import *
from SUAVE.Components.Wings.Segment import Segment
from SUAVE.Input_Output.OpenVSP.vsp_read import vsp_read
from SUAVE.Components.Wings import Main_Wing, Horizontal_Tail, Vertical_Tail
from SUAVE.Components.Energy.Converters import Internal_Combustion_Engine, Propeller
from SUAVE.Components.Energy.Networks import Internal_Combustion_Propeller
from SUAVE.Components.Fuselages import Fuselage
from SUAVE.Components.Nacelles import Nacelle
from SUAVE.Methods.Geometry.Two_Dimensional.Planform import wing_planform
from SUAVE.Methods.Geometry.Two_Dimensional.Planform import horizontal_tail_planform
from SUAVE.Methods.Geometry.Two_Dimensional.Planform import vertical_tail_planform     
from SUAVE.Analyses.Mission.Segments.Segment import Segment
from SUAVE.Analyses.Process import Process
from SUAVE.Analyses.Stability.Fidelity_Zero import Stability
# These are a variety of plotting routines that simplify the plotting process for commonly 
# requested metrics. Plots of specifically desired metrics can also be manually created.
from SUAVE.Methods.Propulsion.turbofan_sizing import turbofan_sizing
from SUAVE.Components.Energy.Networks.Network import Network
# Rather than conventional sizing, this script builds the turbofan energy network. This process is
# covered in more detail in a separate tutorial. It does not size the turbofan geometry.
import vsp as vsp
print(vsp.GetVSPVersion())
from copy import deepcopy

def print_vehicle_state(vehicle):
    print("=== Vehicle Geometry Check ===")
    try:
        print("Main wing area:", vehicle.wings.main_wing.area)
        print("Horizontal tail area:", vehicle.horizontal_tail.area)
        print("Vertical tail area:", vehicle.vertical_tail.area)
        # Estimate tail moment arm (distance from wing AC to tail AC)
        l_f = vehicle.vertical_tail.origin[0][0] - vehicle.wings.main_wing.origin[0][0]
        print("Tail moment arm l_f:", l_f)
    except Exception as e:
        print("Error accessing geometry:", e)
    print("Number of engines:", len(getattr(vehicle, "networks", [])))

def debug_segment(segment):
    print("\n=== Evaluating Segment:", getattr(segment, "tag", "unknown"), "===")
    try:
        state = segment.state
        cond = getattr(state, "conditions", None)
        if cond is not None:
            print("Altitude:", getattr(cond, "altitude", "N/A"))
            print("Mach:", getattr(cond, "mach", "N/A"))
            print("Mass:", getattr(cond, "mass", "N/A"))
        else:
            print("No state.conditions available")
    except Exception as e:
        print("Error accessing segment state:", e)

# ----------------------------
# Patch Segment.evaluate
# ----------------------------
original_evaluate = Segment.evaluate

def evaluate_with_print(self):
    print(f"\n=== Evaluating Segment: {getattr(self,'tag',self)} ===")
    
    # Safely access altitude, mach, mass
    cond = getattr(self.state, 'conditions', None)
    alt  = getattr(cond, 'altitude', None) if cond is not None else None
    mach = getattr(cond, 'mach', None) if cond is not None else None
    mass = getattr(cond, 'mass', None) if cond is not None else None
    print(f"Segment state: altitude={alt}, mach={mach}, mass={mass}")

    
    print(f"Segment state: altitude={alt}, mach={mach}, mass={mass}")
    
    return original_evaluate(self)

Segment.evaluate = evaluate_with_print

# ----------------------------
# Patch Process.evaluate
# ----------------------------
original_process_evaluate = Process.evaluate

def process_with_print(self, *args, **kwargs):
    print(f"--> Running Process Step: {getattr(self, 'tag', 'unknown')}")
    result = original_process_evaluate(self, *args, **kwargs)
    print(f"<-- Completed Process Step: {getattr(self, 'tag', 'unknown')}")
    return result

Process.evaluate = process_with_print

# ----------------------------
# Patch Stability.__call__
# ----------------------------
original_stability_call = Stability.__call__

def stability_with_print(self, conditions):
    print("!!! Computing Stability Derivatives ...")
    try:
        result = original_stability_call(self, conditions)
        print("!!! Stability computation done.")
        return result
    except Exception as e:
        print(f"!!! ERROR in Stability Computation: {e}")
        raise e

Stability.__call__ = stability_with_print

# ----------------------------------------------------------------------
#   Main
# ----------------------------------------------------------------------

def main():
    """This function gets the vehicle configuration, analysis settings, and then runs the mission.
    Once the mission is complete, the results are plotted."""

    # print("Checking tail geometry before mission evaluation:")
    # print("Vertical tail area:", vehicle.vertical_tail.area)
    # print("Tail moment arm (l_f):", vehicle.vertical_tail.origin[0][0] - vehicle.wings.main_wing.origin[0][0])
    # print("Horizontal tail area:", vehicle.horizontal_tail.area)
    # print("Wing area:", vehicle.wings.main_wing.area)
    
    # Extract vehicle configurations and the analysis settings that go with them
    configs, analyses = full_setup()

    vehicle = configs['base']  

    print_vehicle_state(vehicle)

    # Size each of the configurations according to a given set of geometry relations
    simple_sizing(configs)

    # Perform operations needed to make the configurations and analyses usable in the mission
    configs.finalize()
    analyses.finalize()

    # Determine the vehicle weight breakdown (independent of mission fuel usage)
    weights = analyses.configs.base.weights
    breakdown = weights.evaluate()      
    # Perform a mission analysis
    mission = analyses.missions.base
    results = mission.evaluate()

    # Plot all mission results, including items such as altitude profile and L/D
    plot_mission(results)

    return

# ----------------------------------------------------------------------
#   Analysis Setup
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
#   Define the Vehicle Analyses
# ----------------------------------------------------------------------

def analyses_setup(configs):
    """Set up analyses for each of the different configurations."""

    analyses = SUAVE.Analyses.Analysis.Container()

    # Build a base analysis for each configuration. Here the base analysis is always used, but
    # this can be modified if desired for other cases.
    for tag,config in configs.items():
        analysis = base_analysis(config)
        analyses[tag] = analysis

    return analyses

def base_analysis(vehicle):
    """This is the baseline set of analyses to be used with this vehicle. Of these, the most
    commonly changed are the weights and aerodynamics methods."""

    # ------------------------------------------------------------------
    #   Initialize the Analyses
    # ------------------------------------------------------------------     
    analyses = SUAVE.Analyses.Vehicle()

    # ------------------------------------------------------------------
    #  Weights
    weights = SUAVE.Analyses.Weights.Weights_Transport()
    weights.vehicle = vehicle
    analyses.append(weights)

    # ------------------------------------------------------------------
    #  Aerodynamics Analysis
    print("Vehicle wings at aerodynamics creation:", vehicle.wings.keys())
    aerodynamics = SUAVE.Analyses.Aerodynamics.Fidelity_Zero()
    aerodynamics.geometry = vehicle
    analyses.append(aerodynamics)

    # ------------------------------------------------------------------
    #  Stability Analysis
    stability = SUAVE.Analyses.Stability.Fidelity_Zero()
    stability.geometry = vehicle
    analyses.append(stability)

    # ------------------------------------------------------------------
    #  Energy
    energy = SUAVE.Analyses.Energy.Energy()
    energy.network = vehicle.networks
    analyses.append(energy)

    # ------------------------------------------------------------------
    #  Planet Analysis
    planet = SUAVE.Analyses.Planets.Planet()
    analyses.append(planet)

    # ------------------------------------------------------------------
    #  Atmosphere Analysis
    atmosphere = SUAVE.Analyses.Atmospheric.US_Standard_1976()
    atmosphere.features.planet = planet.features
    analyses.append(atmosphere)   

    return analyses    

# ----------------------------------------------------------------------
#   Define the Vehicle
# ----------------------------------------------------------------------

import xml.etree.ElementTree as ET

def vehicle_setup(vsp3_file=r'C:\Users\OHAGANLU\SUAVE\Tutorials-2.5.2\ATR72-600.vsp3'):
    """
    Vehicle setup using VSP3 geometry.
    Automatically populates SUAVE parameters using SUAVE naming conventions.
    """
    
    # ------------------------------------------------------------------
    #   Read VSP3 geometry
    # ------------------------------------------------------------------  
    vehicle = vsp_read(vsp3_file, units_type='SI', specified_network=False)
    vehicle.tag = 'ATR_72-600'

    # Vehicle level mass properties
    # The maximum takeoff gross weight is used by a number of methods, most notably the weight
    # method. However, it does not directly inform mission analysis.
    vehicle.mass_properties.max_takeoff               = 22800 * Units.kilogram 
    # The takeoff weight is used to determine the weight of the vehicle at the start of the mission
    vehicle.mass_properties.takeoff                   = 22800 * Units.kilogram   
    # Operating empty may be used by various weight methods or other methods. Importantly, it does
    # not constrain the mission analysis directly, meaning that the vehicle weight in a mission
    # can drop below this value if more fuel is needed than is available.
    vehicle.mass_properties.operating_empty           = 13010 * Units.kilogram 
    # The maximum zero fuel weight is also used by methods such as weights
    vehicle.mass_properties.max_zero_fuel             = 20800 * Units.kilogram
    # Cargo weight typically feeds directly into weights output and does not affect the mission
    vehicle.mass_properties.cargo                     = 7550.  * Units.kilogram

    vehicle.envelope.ultimate_load = 3.75
    vehicle.envelope.limit_load    = 2.5

    vehicle.systems.control        = "fully powered" 
    vehicle.systems.accessories    = "medium range"

    vehicle.reference_area = 61.0 * Units['meters**2']
    
    # ------------------------------------------------------------------
    #   Main Wing
    # ------------------------------------------------------------------
    wing_vsp = vehicle.wings.wing
    wing = Main_Wing()
    wing.tag = 'main_wing'

    # Populate SUAVE parameters using VSP values (example mapping)
    wing.aspect_ratio = wing_vsp.aspect_ratio
    print("VSP Wing Aspect Ratio:", wing_vsp.aspect_ratio)
    wing.sweeps.quarter_chord = wing_vsp.sweeps.quarter_chord
    wing.thickness_to_chord = wing_vsp.thickness_to_chord
    wing.taper = wing_vsp.taper
    wing.spans.projected = wing_vsp.spans.projected
    wing.chords.root = wing_vsp.chords.root
    wing.chords.tip = wing_vsp.chords.tip
    wing.chords.mean_aerodynamic = wing_vsp.chords.mean_aerodynamic
    wing.areas.reference = wing_vsp.areas.reference
    wing.twists.root = wing_vsp.twists.root
    wing.twists.tip = wing_vsp.twists.tip
    wing.origin = wing_vsp.origin
    wing.vertical = False
    wing.symmetric = True
    wing.high_lift = True
    wing.dynamic_pressure_ratio = 1.0
    wing.areas.wetted = 61 * Units['meters**2']
    
    # Optional: add control surfaces if desired
    # wing.append_control_surface(...)
    
    vehicle.append_component(wing)
    
    # ------------------------------------------------------------------
    #   Horizontal Stabilizer
    # ------------------------------------------------------------------
    htail_vsp = vehicle.wings.htail
    htail = Horizontal_Tail()
    htail.tag = 'horizontal_stabilizer'
    
    htail.aspect_ratio = htail_vsp.aspect_ratio
    htail.sweeps.quarter_chord = htail_vsp.sweeps.quarter_chord
    htail.thickness_to_chord = htail_vsp.thickness_to_chord
    htail.taper = htail_vsp.taper
    htail.spans.projected = htail_vsp.spans.projected
    htail.chords.root = htail_vsp.chords.root
    htail.chords.tip = htail_vsp.chords.tip
    htail.chords.mean_aerodynamic = htail_vsp.chords.mean_aerodynamic
    htail.areas.reference = htail_vsp.areas.reference
    htail.twists.root = htail_vsp.twists.root
    htail.twists.tip = htail_vsp.twists.tip
    htail.origin = htail_vsp.origin
    htail.vertical = False
    htail.symmetric = True
    htail.dynamic_pressure_ratio = 0.9
    
    vehicle.append_component(htail)
    
    # ------------------------------------------------------------------
    #   Vertical Stabilizer
    # ------------------------------------------------------------------
    vtail_vsp = vehicle.wings.vtail
    vtail = Vertical_Tail()
    vtail.tag = 'vertical_stabilizer'
    
    vtail.aspect_ratio = vtail_vsp.aspect_ratio
    print("VSP Vtail Aspect Ratio:", vtail_vsp.aspect_ratio)
    vtail.sweeps.quarter_chord = vtail_vsp.sweeps.quarter_chord
    vtail.thickness_to_chord = vtail_vsp.thickness_to_chord
    vtail.taper = vtail_vsp.taper
    vtail.spans.projected = vtail_vsp.spans.projected
    vtail.chords.root = vtail_vsp.chords.root
    vtail.chords.tip = vtail_vsp.chords.tip
    vtail.chords.mean_aerodynamic = vtail_vsp.chords.mean_aerodynamic
    vtail.areas.reference = vtail_vsp.areas.reference
    print("VSP Vtail Reference Area:", vtail_vsp.areas.reference)
    vtail.twists.root = vtail_vsp.twists.root
    vtail.twists.tip = vtail_vsp.twists.tip
    vtail.origin = vtail_vsp.origin
    vtail.vertical = True
    vtail.symmetric = False
    vtail.t_tail = False
    vtail.dynamic_pressure_ratio = 1.0

    vehicle.append_component(vtail)
    
    
    # ------------------------------------------------------------------
    #   Fuselage
    # ------------------------------------------------------------------
    fuse_vsp = vehicle.fuselages.fuselage_1
    fuselage = Fuselage()
    fuselage.tag = 'fuselage'
    
    fuselage.number_coach_seats = vehicle.passengers
    fuselage.seats_abreast = 6
    fuselage.seat_pitch = 1.0 * Units.meter
    fuselage.fineness.nose = 1.6
    fuselage.fineness.tail = 2.0
    fuselage.lengths.nose = fuse_vsp.lengths.nose
    fuselage.lengths.tail = fuse_vsp.lengths.tail
    fuselage.lengths.total = fuse_vsp.lengths.total
    fuselage.lengths.fore_space = 6.0 * Units.meter
    fuselage.lengths.aft_space = 5.0 * Units.meter
    fuselage.width = fuse_vsp.width
    fuselage.heights.maximum = fuse_vsp.heights.maximum
    fuselage.effective_diameter = fuse_vsp.width
    fuselage.areas.side_projected = fuse_vsp.areas.side_projected
    fuselage.areas.wetted = fuse_vsp.areas.wetted
    fuselage.areas.front_projected = fuse_vsp.areas.front_projected
    fuselage.differential_pressure = 5.0e4 * Units.pascal
    fuselage.heights.at_quarter_length = fuse_vsp.heights.at_quarter_length
    fuselage.heights.at_three_quarters_length = fuse_vsp.heights.at_three_quarters_length
    fuselage.heights.at_wing_root_quarter_chord = fuse_vsp.heights.at_wing_root_quarter_chord
    
    vehicle.append_component(fuselage)

    nacelle1 = Nacelle()
    nacelle1.tag = 'nacelle1'
    nacelle1.length = 1.5 * Units.meter
    nacelle1.diameter = 0.863* Units.meter
    nacelle1.inlet_diameter = 0.75 * Units.meter
    nacelle1.area = 3.14 * (nacelle1.diameter / 2)**2
    nacelle1.origin = [[10.162 * Units.meter, 4.104 * Units.meter, 1.014 * Units.meter]]# Position the nacelle appropriately

    vehicle.append_component(nacelle1)

    nacelle2 = Nacelle()
    nacelle2.tag = 'nacelle2'
    nacelle2.length = 1.5 * Units.meter
    nacelle2.diameter = 0.863 * Units.meter
    nacelle2.inlet_diameter = 0.75 * Units.meter
    nacelle2.area = 3.14 * (nacelle2.diameter / 2)**2
    nacelle2.origin = [[10.162 * Units.meter, -4.104 * Units.meter, 1.014 * Units.meter]]# Position the nacelle appropriately

    vehicle.append_component(nacelle2)

    turbofan = SUAVE.Components.Energy.Networks.Turbofan()
    # For some methods, the 'turbofan' tag is still necessary. This will be changed in the
    # future to allow arbitrary tags.
    turbofan.tag = 'turbofan'
    
    # High-level setup
    turbofan.number_of_engines = 2
    turbofan.bypass_ratio      = 5.4
    turbofan.origin            = [[10.162, 4.104,1.014],[10.162, -4.104,1.104]] * Units.meter

    # Establish the correct working fluid
    turbofan.working_fluid = SUAVE.Attributes.Gases.Air()
    
    # Components use estimated efficiencies. Estimates by technology level can be
    # found in textbooks such as those by J.D. Mattingly
    
    # ------------------------------------------------------------------
    #   Component 1 - Ram
    
    # Converts freestream static to stagnation quantities
    ram = SUAVE.Components.Energy.Converters.Ram()
    ram.tag = 'ram'
    
    # add to the network
    turbofan.append(ram)

    # ------------------------------------------------------------------
    #  Component 2 - Inlet Nozzle
    
    # Create component
    inlet_nozzle = SUAVE.Components.Energy.Converters.Compression_Nozzle()
    inlet_nozzle.tag = 'inlet_nozzle'
    
    # Specify performance
    inlet_nozzle.polytropic_efficiency = 0.98
    inlet_nozzle.pressure_ratio        = 0.98
    
    # Add to network
    turbofan.append(inlet_nozzle)
    
    # ------------------------------------------------------------------
    #  Component 3 - Low Pressure Compressor
    
    # Create component
    compressor = SUAVE.Components.Energy.Converters.Compressor()    
    compressor.tag = 'low_pressure_compressor'

    # Specify performance
    compressor.polytropic_efficiency = 0.91
    compressor.pressure_ratio        = 1.14    
    
    # Add to network
    turbofan.append(compressor)
    
    # ------------------------------------------------------------------
    #  Component 4 - High Pressure Compressor
    
    # Create component
    compressor = SUAVE.Components.Energy.Converters.Compressor()    
    compressor.tag = 'high_pressure_compressor'
    
    # Specify performance
    compressor.polytropic_efficiency = 0.91
    compressor.pressure_ratio        = 13.415    
    
    # Add to network
    turbofan.append(compressor)

    # ------------------------------------------------------------------
    #  Component 5 - Low Pressure Turbine
    
    # Create component
    turbine = SUAVE.Components.Energy.Converters.Turbine()   
    turbine.tag='low_pressure_turbine'
    
    # Specify performance
    turbine.mechanical_efficiency = 0.99
    turbine.polytropic_efficiency = 0.93     
    
    # Add to network
    turbofan.append(turbine)
      
    # ------------------------------------------------------------------
    #  Component 6 - High Pressure Turbine
    
    # Create component
    turbine = SUAVE.Components.Energy.Converters.Turbine()   
    turbine.tag='high_pressure_turbine'

    # Specify performance
    turbine.mechanical_efficiency = 0.99
    turbine.polytropic_efficiency = 0.93     
    
    # Add to network
    turbofan.append(turbine)  
    
    # ------------------------------------------------------------------
    #  Component 7 - Combustor
    
    # Create component    
    combustor = SUAVE.Components.Energy.Converters.Combustor()   
    combustor.tag = 'combustor'
    
    # Specify performance
    combustor.efficiency                = 0.99 
    combustor.alphac                    = 1.0   
    combustor.turbine_inlet_temperature = 1450 # K
    combustor.pressure_ratio            = 0.95
    combustor.fuel_data                 = SUAVE.Attributes.Propellants.Jet_A()    
    
    # Add to network
    turbofan.append(combustor)

    # ------------------------------------------------------------------
    #  Component 8 - Core Nozzle
    
    # Create component
    nozzle = SUAVE.Components.Energy.Converters.Expansion_Nozzle()   
    nozzle.tag = 'core_nozzle'
    
    # Specify performance
    nozzle.polytropic_efficiency = 0.95
    nozzle.pressure_ratio        = 0.99    
    
    # Add to network
    turbofan.append(nozzle)

    # ------------------------------------------------------------------
    #  Component 9 - Fan Nozzle
    
    # Create component
    nozzle = SUAVE.Components.Energy.Converters.Expansion_Nozzle()   
    nozzle.tag = 'fan_nozzle'

    # Specify performance
    nozzle.polytropic_efficiency = 0.95
    nozzle.pressure_ratio        = 0.99    
    
    # Add to network
    turbofan.append(nozzle)
    
    # ------------------------------------------------------------------
    #  Component 10 - Fan
    
    # Create component
    fan = SUAVE.Components.Energy.Converters.Fan()   
    fan.tag = 'fan'

    # Specify performance
    fan.polytropic_efficiency = 0.93
    fan.pressure_ratio        = 1.7    
    
    # Add to network
    turbofan.append(fan)
    
    # ------------------------------------------------------------------
    #  Component 11 - thrust (to compute the thrust)
    
    thrust = SUAVE.Components.Energy.Processes.Thrust()       
    thrust.tag ='compute_thrust'
 
    # Design thrust is used to determine mass flow at full throttle
    thrust.total_design             = 2*5000. * Units.N #Newtons
    
    # Add to network
    turbofan.thrust = thrust
    
    # Design sizing conditions are also used to determine mass flow
    altitude      = 25000.0*Units.ft
    mach_number   = 0.7    

    # Determine turbofan behavior at the design condition
    turbofan_sizing(turbofan,mach_number,altitude)   
    
    # Add turbofan network to the vehicle 
    vehicle.append_component(turbofan)      

    plot_vehicle(vehicle)
    
    return vehicle

# def vehicle_setup():
#     # This function creates the vehicle object for the ATR 72-600. It is broken into a separate
#     # function to keep the tutorial organized, but this is not required. Note that some of the
#     # values used here are estimates or approximations based on available public data. This is
#     # sufficient for demonstration purposes, but should not be used for analysis requiring hig
    
#     # ------------------------------------------------------------------
#     #   Initialize the Vehicle
#     # ------------------------------------------------------------------    
    
#     vehicle = vsp_read(
#         r'C:\Users\OHAGANLU\SUAVE\Tutorials-2.5.2\ATR72-600.vsp3',
#         units_type='SI',
#         specified_network=False
#     )
#     vehicle.tag = 'ATR_72-600'

#     # --- Print imported components for verification ---
#     print("Imported Wings:")
#     for tag, wing in vehicle.wings.items():
#         print(f"  {tag}")
#     print("Imported Fuselages:")
#     for tag, fuse in vehicle.fuselages.items():
#         print(f"  {tag}")
#     print("Imported Nacelles:")
#     for tag, nac in vehicle.nacelles.items():
#         print(f"  {tag}")

#     # --- Map wings to SUAVE-standard objects ---

#     # Main wing
#     wing_vsp = vehicle.wings.wing
#     main_wing = SUAVE.Components.Wings.Main_Wing()
#     main_wing.tag = 'main_wing'
#     main_wing.spans = wing_vsp.spans
#     main_wing.chords = wing_vsp.chords
#     main_wing.sweeps.quarter_chord = wing_vsp.sweeps.quarter_chord
#     main_wing.dihedral = wing_vsp.dihedral 
#     # main_wing.airfoil = wing_vsp.airfoil
#     main_wing.twists.root = wing_vsp.twists.root
#     vehicle.wings.main_wing = main_wing

#     # Horizontal stabilizer
#     htail_vsp = vehicle.wings.htail
#     htail = SUAVE.Components.Wings.Horizontal_Tail()
#     htail.tag = 'horizontal_stabilizer'
#     htail.spans = htail_vsp.spans
#     htail.chords = htail_vsp.chords
#     htail.sweeps.quarter_chord = htail_vsp.sweeps.quarter_chord
#     htail.dihedral = htail_vsp.dihedral
#     # htail.airfoil = htail_vsp.airfoil
#     htail.twists.root = htail_vsp.twists.root
#     vehicle.wings.horizontal_stabilizer = htail

#     # Vertical stabilizer
#     vtail_vsp = vehicle.wings.vtail
#     vtail = SUAVE.Components.Wings.Vertical_Tail()
#     vtail.tag = 'vertical_stabilizer'
#     vtail.spans = vtail_vsp.spans
#     vtail.chords = vtail_vsp.chords
#     vtail.sweeps.quarter_chord = vtail_vsp.sweeps.quarter_chord
#     vtail.dihedral = vtail_vsp.dihedral
#     # vtail.airfoil = vtail_vsp.airfoil
#     vtail.twists.root = vtail_vsp.twists.root
#     vehicle.wings.vertical_stabilizer = vtail

#     # --- Map fuselage ---
#     fuse_vsp = vehicle.fuselages.fuselage_1
#     fuselage = SUAVE.Components.Fuselages.Fuselage()
#     fuselage.tag = 'fuselage'
#     fuselage.lengths = fuse_vsp.lengths
#     fuselage.width = fuse_vsp.width
#     fuselage.heights = fuse_vsp.heights
#     vehicle.fuselages.fuselage = fuselage

#     # --- Optional: cleanup old VSP keys ---
#     for key in ['wing', 'htail', 'vtail']:
#         if key in vehicle.wings:
#             del vehicle.wings[key]
#     if 'fuselage_1' in vehicle.fuselages:
#         del vehicle.fuselages['fuselage_1']

#     # Vehicle level parameters
#     # The vehicle reference area typically matches the main wing reference area 
#     vehicle.reference_area         = 61 * Units['meters**2']  
#     # Number of passengers, control settings, and accessories settings are used by the weights
#     # methods
#     vehicle.passengers             = 72
#     vehicle.systems.control        = "fully powered" 
#     vehicle.systems.accessories    = "medium range"  

#     # --- Keep only nacelle geometry ---
#     nacelle_networks = []
#     for net in vehicle.networks:
#         if 'nacelle' in net.tag.lower() or 'engine' in net.tag.lower():
#             nacelle_networks.append(net)

#     # Replace vehicle networks with only nacelles
#     vehicle.networks = nacelle_networks

#     print("Imported nacelle geometries:")
#     for net in vehicle.networks:
#         print("  ", net.tag)

#     nacelle1 = Nacelle()
#     nacelle1.tag = 'nacelle1'
#     nacelle1.length = 1.5 * Units.meter
#     nacelle1.diameter = 0.863* Units.meter
#     nacelle1.inlet_diameter = 0.75 * Units.meter
#     nacelle1.area = 3.14 * (nacelle1.diameter / 2)**2
#     nacelle1.origin = [[10.162 * Units.meter, 4.104 * Units.meter, 1.014 * Units.meter]]# Position the nacelle appropriately

#     vehicle.append_component(nacelle1)

#     nacelle2 = Nacelle()
#     nacelle2.tag = 'nacelle2'
#     nacelle2.length = 1.5 * Units.meter
#     nacelle2.diameter = 0.863 * Units.meter
#     nacelle2.inlet_diameter = 0.75 * Units.meter
#     nacelle2.area = 3.14 * (nacelle2.diameter / 2)**2
#     nacelle2.origin = [[10.162 * Units.meter, -4.104 * Units.meter, 1.014 * Units.meter]]# Position the nacelle appropriately

#     vehicle.append_component(nacelle2)
    
#     # ------------------------------------------------------------------
#     #   Vehicle-level Properties
#     # ------------------------------------------------------------------    

#     # Vehicle level mass properties
#     # The maximum takeoff gross weight is used by a number of methods, most notably the weight
#     # method. However, it does not directly inform mission analysis.
#     vehicle.mass_properties.max_takeoff               = 22800 * Units.kilogram 
#     # The takeoff weight is used to determine the weight of the vehicle at the start of the mission
#     vehicle.mass_properties.takeoff                   = 22800 * Units.kilogram   
#     # Operating empty may be used by various weight methods or other methods. Importantly, it does
#     # not constrain the mission analysis directly, meaning that the vehicle weight in a mission
#     # can drop below this value if more fuel is needed than is available.
#     vehicle.mass_properties.operating_empty           = 13010 * Units.kilogram 
#     # The maximum zero fuel weight is also used by methods such as weights
#     vehicle.mass_properties.max_zero_fuel             = 20800 * Units.kilogram
#     # Cargo weight typically feeds directly into weights output and does not affect the mission
#     vehicle.mass_properties.cargo                     = 7550.  * Units.kilogram   
    
#     # Envelope properties
#     # These values are typical FAR values for a transport of this type
#     vehicle.envelope.ultimate_load = 3.75
#     vehicle.envelope.limit_load    = 2.5

#     for wing in vehicle.wings.values():
#         wing.areas = wing_planform(wing)

#     # ------------------------------------------------------------------
#     #   Vehicle Definition Complete
#     # ------------------------------------------------------------------
#     plot_vehicle(vehicle)
#     plot_vehicle_vlm_panelization(vehicle)   

    
#     return vehicle

def full_setup():
    """This function gets the baseline vehicle and creates modifications for different 
    configurations, as well as the mission and analyses to go with those configurations."""

    # Collect baseline vehicle data and changes when using different configuration settings
    vehicle  = vehicle_setup()
    configs  = configs_setup(vehicle)

    # Get the analyses to be used when different configurations are evaluated
    configs_analyses = analyses_setup(configs)

    # Create the mission that will be flown
    mission  = mission_setup(configs_analyses)
    missions_analyses = missions_setup(mission)

    # Add the analyses to the proper containers
    analyses = SUAVE.Analyses.Analysis.Container()
    analyses.configs  = configs_analyses
    analyses.missions = missions_analyses

    return configs, analyses

# ----------------------------------------------------------------------
#   Define the Configurations
# ---------------------------------------------------------------------

def configs_setup(vehicle):
    """This function sets up vehicle configurations for use in different parts of the mission.
    Here, this is mostly in terms of high lift settings."""
    
    # ------------------------------------------------------------------
    #   Initialize Configurations
    # ------------------------------------------------------------------
    configs = SUAVE.Components.Configs.Config.Container()

    base_config = SUAVE.Components.Configs.Config(vehicle)
    base_config.tag = 'base'
    configs.append(base_config)

    # ------------------------------------------------------------------
    #   Cruise Configuration
    # ------------------------------------------------------------------
    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'cruise'
    configs.append(config)

    # ------------------------------------------------------------------
    #   Takeoff Configuration
    # ------------------------------------------------------------------
    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'takeoff'
    # config.wings['main_wing'].control_surfaces.flap.deflection = 20. * Units.deg
    # config.wings['main_wing'].control_surfaces.slat.deflection = 25. * Units.deg
    # A max lift coefficient factor of 1 is the default, but it is highlighted here as an option
    config.max_lift_coefficient_factor    = 1.

    configs.append(config)
    
    # ------------------------------------------------------------------
    #   Cutback Configuration
    # ------------------------------------------------------------------
    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'cutback'
    # config.wings['main_wing'].control_surfaces.flap.deflection = 20. * Units.deg
    # config.wings['main_wing'].control_surfaces.slat.deflection = 20. * Units.deg
    config.max_lift_coefficient_factor    = 1.

    configs.append(config)    

    # ------------------------------------------------------------------
    #   Landing Configuration
    # ------------------------------------------------------------------

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'landing'

    # config.wings['main_wing'].control_surfaces.flap.deflection = 30. * Units.deg
    # config.wings['main_wing'].control_surfaces.slat.deflection = 25. * Units.deg  
    config.max_lift_coefficient_factor    = 1. 

    configs.append(config)

    # ------------------------------------------------------------------
    #   Short Field Takeoff Configuration
    # ------------------------------------------------------------------ 

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'short_field_takeoff'
    
    # config.wings['main_wing'].control_surfaces.flap.deflection = 20. * Units.deg
    # config.wings['main_wing'].control_surfaces.slat.deflection = 20. * Units.deg
    config.max_lift_coefficient_factor    = 1. 
  
    configs.append(config)

    return configs

def simple_sizing(configs):
    """This function applies a few basic geometric sizing relations and modifies the landing
    configuration."""

    base = configs.base
    # Update the baseline data structure to prepare for changes
    base.pull_base()

    # Revise the zero fuel weight. This will only affect the base configuration. To do all
    # configurations, this should be specified in the top level vehicle definition.
    base.mass_properties.max_zero_fuel = 0.9 * base.mass_properties.max_takeoff 

    # Estimate wing areas
    for wing in base.wings:
        wing.areas.wetted   = 2.0 * wing.areas.reference
        wing.areas.exposed  = 0.8 * wing.areas.wetted
        wing.areas.affected = 0.6 * wing.areas.wetted

    # Store how the changes compare to the baseline configuration
    base.store_diff()

    # ------------------------------------------------------------------
    #   Landing Configuration
    # ------------------------------------------------------------------
    landing = configs.landing

    # Make sure base data is current
    landing.pull_base()

    # Add a landing weight parameter. This is used in field length estimation and in
    # initially the landing mission segment type.
    landing.mass_properties.landing = 0.85 * base.mass_properties.takeoff

    # Store how the changes compare to the baseline configuration
    landing.store_diff()

    return

# ----------------------------------------------------------------------
#   Define the Mission
# ----------------------------------------------------------------------

def mission_setup(analyses):
    """This function defines the baseline mission that will be flown by the aircraft in order
    to compute performance."""

    # ------------------------------------------------------------------
    #   Initialize the Mission
    # ------------------------------------------------------------------

    mission = SUAVE.Analyses.Mission.Sequential_Segments()
    mission.tag = 'the_mission'

    # Airport
    # The airport parameters are used in calculating field length and noise. They are not
    # directly used in mission performance estimation
    airport = SUAVE.Attributes.Airports.Airport()
    airport.altitude   =  0.0  * Units.ft
    airport.delta_isa  =  0.0
    airport.atmosphere = SUAVE.Attributes.Atmospheres.Earth.US_Standard_1976()

    mission.airport = airport    

    # Unpack Segments module
    Segments = SUAVE.Analyses.Mission.Segments

    # Base segment 
    base_segment = Segments.Segment()

    # ------------------------------------------------------------------
    #   First Climb Segment: Constant Speed, Constant Rate
    # ------------------------------------------------------------------

    # A constant speed, constant rate climb segment is used first. This means that the aircraft
    # will maintain a constant airspeed and constant climb rate until it hits the end altitude.
    # For this type of segment, the throttle is allowed to vary as needed to match required
    # performance.
    segment = Segments.Climb.Constant_Speed_Constant_Rate(base_segment)
    # It is important that all segment tags must be unique for proper evaluation. At the moment 
    # this is not automatically enforced. 
    segment.tag = "climb_1"

    # The analysis settings for mission segment are chosen here. These analyses include information
    # on the vehicle configuration.
    segment.analyses.extend( analyses.takeoff )

    segment.altitude_start = 0.0   * Units.km
    segment.altitude_end   = 3.0   * Units.km
    segment.air_speed      = 125.0 * Units['m/s']
    segment.climb_rate     = 6.0   * Units['m/s']

    # Add to misison
    mission.append_segment(segment)

    # ------------------------------------------------------------------
    #   Second Climb Segment: Constant Speed, Constant Rate
    # ------------------------------------------------------------------    

    segment = Segments.Climb.Constant_Speed_Constant_Rate(base_segment)
    segment.tag = "climb_2"

    segment.analyses.extend( analyses.cruise )

    # A starting altitude is no longer needed as it will automatically carry over from the
    # previous segment. However, it could be specified if desired. This would potentially cause
    # a jump in altitude but would otherwise not cause any problems.
    segment.altitude_end   = 8.0   * Units.km
    segment.air_speed      = 190.0 * Units['m/s']
    segment.climb_rate     = 6.0   * Units['m/s']

    # Add to mission
    mission.append_segment(segment)

    # ------------------------------------------------------------------
    #   Third Climb Segment: constant Speed, Constant Rate
    # ------------------------------------------------------------------    

    segment = Segments.Climb.Constant_Speed_Constant_Rate(base_segment)
    segment.tag = "climb_3"

    segment.analyses.extend( analyses.cruise )

    segment.altitude_end = 10.668 * Units.km
    segment.air_speed    = 226.0  * Units['m/s']
    segment.climb_rate   = 3.0    * Units['m/s']

    # Add to mission
    mission.append_segment(segment)

    # ------------------------------------------------------------------    
    #   Cruise Segment: Constant Speed, Constant Altitude
    # ------------------------------------------------------------------    

    segment = Segments.Cruise.Constant_Speed_Constant_Altitude(base_segment)
    segment.tag = "cruise"

    segment.analyses.extend( analyses.cruise )

    segment.air_speed  = 230.412 * Units['m/s']
    segment.distance   = 2490. * Units.nautical_miles

    # Add to mission
    mission.append_segment(segment)

    # ------------------------------------------------------------------
    #   First Descent Segment: Constant Speed, Constant Rate
    # ------------------------------------------------------------------

    segment = Segments.Descent.Constant_Speed_Constant_Rate(base_segment)
    segment.tag = "descent_1"

    segment.analyses.extend( analyses.cruise )

    segment.altitude_end = 8.0   * Units.km
    segment.air_speed    = 220.0 * Units['m/s']
    segment.descent_rate = 4.5   * Units['m/s']

    # Add to mission
    mission.append_segment(segment)

    # ------------------------------------------------------------------
    #   Second Descent Segment: Constant Speed, Constant Rate
    # ------------------------------------------------------------------

    segment = Segments.Descent.Constant_Speed_Constant_Rate(base_segment)
    segment.tag = "descent_2"

    segment.analyses.extend( analyses.landing )

    segment.altitude_end = 6.0   * Units.km
    segment.air_speed    = 195.0 * Units['m/s']
    segment.descent_rate = 5.0   * Units['m/s']

    # Add to mission
    mission.append_segment(segment)

    # ------------------------------------------------------------------
    #   Third Descent Segment: Constant Speed, Constant Rate
    # ------------------------------------------------------------------

    segment = Segments.Descent.Constant_Speed_Constant_Rate(base_segment)
    segment.tag = "descent_3"

    segment.analyses.extend( analyses.landing )
    # While it is set to zero here and therefore unchanged, a drag increment can be used if
    # desired. This can avoid negative throttle values if drag generated by the base airframe
    # is insufficient for the desired descent speed and rate.
    analyses.landing.aerodynamics.settings.spoiler_drag_increment = 0.00

    segment.altitude_end = 4.0   * Units.km
    segment.air_speed    = 170.0 * Units['m/s']
    segment.descent_rate = 5.0   * Units['m/s']

    # Add to mission
    mission.append_segment(segment)

    # ------------------------------------------------------------------
    #   Fourth Descent Segment: Constant Speed, Constant Rate
    # ------------------------------------------------------------------

    segment = Segments.Descent.Constant_Speed_Constant_Rate(base_segment)
    segment.tag = "descent_4"

    segment.analyses.extend( analyses.landing )
    analyses.landing.aerodynamics.settings.spoiler_drag_increment = 0.00

    segment.altitude_end = 2.0   * Units.km
    segment.air_speed    = 150.0 * Units['m/s']
    segment.descent_rate = 5.0   * Units['m/s']

    # Add to mission
    mission.append_segment(segment)

    # ------------------------------------------------------------------
    #   Fifth Descent Segment: Constant Speed, Constant Rate
    # ------------------------------------------------------------------

    segment = Segments.Descent.Constant_Speed_Constant_Rate(base_segment)
    segment.tag = "descent_5"

    segment.analyses.extend( analyses.landing )
    analyses.landing.aerodynamics.settings.spoiler_drag_increment = 0.00

    segment.altitude_end = 0.0   * Units.km
    segment.air_speed    = 145.0 * Units['m/s']
    segment.descent_rate = 3.0   * Units['m/s']

    # Append to mission
    mission.append_segment(segment)

    # ------------------------------------------------------------------
    #   Mission definition complete    
    # ------------------------------------------------------------------

    return mission

def missions_setup(base_mission):
    """This allows multiple missions to be incorporated if desired, but only one is used here."""

    # Setup the mission container
    missions = SUAVE.Analyses.Mission.Mission.Container()

    # ------------------------------------------------------------------
    #   Base Mission
    # ------------------------------------------------------------------

    # Only one mission (the base mission) is defined in this case
    missions.base = base_mission

    return missions  

# ----------------------------------------------------------------------
#   Plot Mission
# ----------------------------------------------------------------------

def plot_mission(results,line_style='bo-'):
    """This function plots the results of the mission analysis and saves those results to 
    png files."""

    # Plot Flight Conditions 
    plot_flight_conditions(results, line_style)
    
    # Plot Aerodynamic Forces 
    plot_aerodynamic_forces(results, line_style)
    
    # Plot Aerodynamic Coefficients 
    plot_aerodynamic_coefficients(results, line_style)
    
    # Drag Components
    plot_drag_components(results, line_style)
    
    # Plot Altitude, sfc, vehicle weight 
    plot_altitude_sfc_weight(results, line_style)
    
    # Plot Velocities 
    plot_aircraft_velocities(results, line_style)      
        
    return

# This section is needed to actually run the various functions in the file
if __name__ == '__main__': 
    main()    
    # The show commands makes the plots actually appear
    plt.show()