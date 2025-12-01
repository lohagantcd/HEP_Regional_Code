
import numpy as np
import matplotlib.pyplot as plt
import SUAVE
import os

assert SUAVE.__version__=='2.5.2', 'These tutorials only work with the SUAVE 2.5.2 release'
from SUAVE.Core import Data, Units 
import time
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
from SUAVE.Methods.Propulsion.turbofan_sizing import turbofan_sizing
from SUAVE.Components.Energy.Networks.Network import Network
# from SUAVE.Analyses.Mission.Segments.Descent import Linear_Mach_Constant_Rate
# from SUAVE.Methods.Missions.Segments.Descent import Linear_Mach_Constant_Rate

import vsp as vsp
print(vsp.GetVSPVersion())
from copy import deepcopy


def main():

    startTime = time.time()

    with open("C:\\Users\\Luke TCD Woek\\OneDrive - Trinity College Dublin\\Opensky_Flights\\FlightsAC.txt", 'r') as file:
        FlightsAC = np.genfromtxt(file, dtype='str')
        print(FlightsAC)

    with open("C:\\Users\\Luke TCD Woek\\OneDrive - Trinity College Dublin\\Opensky_Flights\\FlightsFN.txt", 'r') as file:
        FlightsFN = np.genfromtxt(file, dtype='str')
        print(FlightsFN)

    with open("C:\\Users\\Luke TCD Woek\\OneDrive - Trinity College Dublin\\Opensky_Flights\\FlightsTOW.txt", 'r') as file:
        FlightsTOW = np.loadtxt(file)
        print(FlightsTOW)

    # with open(r"C:\Users\OHAGANLU\OneDrive - Trinity College Dublin\Opensky_Flights\FlightsAC.txt", 'r') as file:
    #     FlightsAC = np.genfromtxt(file, dtype='str')
    #     print(FlightsAC)

    # with open(r"C:\Users\OHAGANLU\OneDrive - Trinity College Dublin\Opensky_Flights\FlightsFN.txt", 'r') as file:
    #     FlightsFN = np.genfromtxt(file, dtype='str')
    #     print(FlightsFN)

    # with open(r"C:\Users\OHAGANLU\OneDrive - Trinity College Dublin\Opensky_Flights\FlightsTOW.txt", 'r') as file:
    #     FlightsTOW = np.loadtxt(file)
    #     print(FlightsTOW)
    # Only using one flight for testing so dont need this at the moment
    AC_reg = FlightsAC[0]
    Flight_No = FlightsFN[0]
    TOW = FlightsTOW[0]

    # AC_reg = FlightsAC
    # Flight_No = FlightsFN
    # TOW = FlightsTOW

    vehicle, configs = full_setup_1(TOW)

    for i in range(len(FlightsAC)):
        
        AC_reg = FlightsAC[i]
        print("AC reg: ", AC_reg)
        Flight_No = FlightsFN[i]
        print("Flight No: ", Flight_No)
        TOW = FlightsTOW[i]

        vehicle, analyses = full_setup_2(vehicle, configs, AC_reg, Flight_No, TOW)

        simple_sizing(configs)

        configs.finalize()
        analyses.finalize()

        mission = analyses.missions.base
        
        results = mission.evaluate()

        plot_mission(results, AC_reg, Flight_No, TOW)

    endTime = time.time()
    
    print((endTime-startTime)/60)

    return

def full_setup_1(TOW):
    """This function gets the baseline vehicle and creates modifications for different 
    configurations, as well as the mission and analyses to go with those configurations."""

    # Collect baseline vehicle data and changes when using different configuration settings
    vehicle  = vehicle_setup(TOW)
    configs  = configs_setup(vehicle)

    return vehicle, configs

def full_setup_2(vehicle, configs, AC_reg, Flight_No, TOW):
    """This function gets the baseline vehicle and creates modifications for different 
    configurations, as well as the mission and analyses to go with those configurations."""

    vehicle.mass_properties.takeoff = TOW

    # Get the analyses to be used when different configurations are evaluated
    configs_analyses = analyses_setup(configs)

    # Create the mission that will be flown
    mission  = mission_setup(configs_analyses, AC_reg, Flight_No)
    missions_analyses = missions_setup(mission)

    # Add the analyses to the proper containers
    analyses = SUAVE.Analyses.Analysis.Container()
    analyses.configs  = configs_analyses
    analyses.missions = missions_analyses

    return vehicle, analyses

def analyses_setup(configs):

    analyses = SUAVE.Analyses.Analysis.Container()

    for tag,config in configs.items():
        analysis = base_analysis(config)
        analyses[tag] = analysis

    return analyses

def base_analysis(vehicle):
   
    analyses = SUAVE.Analyses.Vehicle()

    weights = SUAVE.Analyses.Weights.Weights_Transport()
    weights.vehicle = vehicle
    analyses.append(weights)

    aerodynamics = SUAVE.Analyses.Aerodynamics.Fidelity_Zero()
    aerodynamics.geometry = vehicle
    analyses.append(aerodynamics)

    stability = SUAVE.Analyses.Stability.Fidelity_Zero()
    stability.geometry = vehicle
    analyses.append(stability)

    energy = SUAVE.Analyses.Energy.Energy()
    energy.network = vehicle.networks
    analyses.append(energy)

    planet = SUAVE.Analyses.Planets.Planet()
    analyses.append(planet)

    atmosphere = SUAVE.Analyses.Atmospheric.US_Standard_1976()
    atmosphere.features.planet = planet.features
    analyses.append(atmosphere)   

    return analyses    

def print_vsp_geometry_summary(vehicle):

    print("\n" + "="*60)
    print(f"=== Vehicle Geometry Summary: {vehicle.tag} ===")
    print("="*60)

    if hasattr(vehicle, "wings") and len(vehicle.wings) > 0:
        print("\n--- Wings ---")
        for tag, wing in vehicle.wings.items():
            print(f"\n[{tag}]")
            print(f"  Type: {'Vertical' if getattr(wing, 'vertical', False) else 'Horizontal'}")
            print(f"  Symmetric: {wing.symmetric}")
            print(f"  Area (ref): {wing.areas.reference/Units['meters**2']:.3f} m²")
            print(f"  Span (proj): {wing.spans.projected/Units.meter:.3f} m")
            print(f"  Aspect ratio: {wing.aspect_ratio:.3f}")
            print(f"  Taper ratio: {wing.taper:.3f}")
            print(f"  Sweep (¼-chord): {wing.sweeps.quarter_chord/Units.deg:.3f}°")
            print(f"  Root chord: {wing.chords.root/Units.meter:.3f} m")
            print(f"  Tip chord: {wing.chords.tip/Units.meter:.3f} m")
            print(f"  MAC: {wing.chords.mean_aerodynamic/Units.meter:.3f} m")
            print(f"  Root twist: {wing.twists.root/Units.deg:.3f}°")
            print(f"  Tip twist: {wing.twists.tip/Units.deg:.3f}°")
            print(f"  Origin: {wing.origin}")
            print(f"  Airfoil count: {len(getattr(wing, 'Airfoils', []))}")

    if hasattr(vehicle, "fuselages") and len(vehicle.fuselages) > 0:
        print("\n--- Fuselages ---")
        for tag, fus in vehicle.fuselages.items():
            print(f"\n[{tag}]")
            print(f"  Length total: {fus.lengths.total/Units.meter:.3f} m")
            print(f"  Max width: {fus.width/Units.meter:.3f} m")
            print(f"  Max height: {fus.heights.maximum/Units.meter:.3f} m")
            print(f"  Wetted area: {fus.areas.wetted/Units['meters**2']:.3f} m²")
            print(f"  Side proj area: {fus.areas.side_projected/Units['meters**2']:.3f} m²")
            print(f"  Frontal area: {fus.areas.front_projected/Units['meters**2']:.3f} m²")
            print(f"  Origin: {fus.origin}")

    if hasattr(vehicle, "nacelles") and len(vehicle.nacelles) > 0:
        print("\n--- Nacelles ---")
        for tag, nac in vehicle.nacelles.items():
            print(f"\n[{tag}]")
            print(f"  Length: {nac.length/Units.meter:.3f} m")
            print(f"  Diameter: {nac.diameter/Units.meter:.3f} m")
            print(f"  Wetted area: {nac.areas.wetted/Units['meters**2']:.3f} m²")
            print(f"  Origin: {nac.origin}")

    if hasattr(vehicle, "propulsors") and len(vehicle.propulsors) > 0:
        print("\n--- Propulsors ---")
        for tag, prop in vehicle.propulsors.items():
            print(f"\n[{tag}]")
            if hasattr(prop, "tag"): print(f"  Type: {prop.tag}")
            if hasattr(prop, "engine_length"): print(f"  Length: {prop.engine_length/Units.meter:.3f} m")
            if hasattr(prop, "nacelle_diameter"): print(f"  Nacelle diam: {prop.nacelle_diameter/Units.meter:.3f} m")
            if hasattr(prop, "origin"): print(f"  Origin: {prop.origin}")

    print("\n" + "="*60)
    print("End of VSP geometry summary\n")
 
def vehicle_setup(TOW):

    vehicle = vsp_read(r"C:\Users\Luke TCD Woek\SUAVE\Tutorials-2.5.2\ATR_72-600\ATR72-600.vsp3", units_type='SI', specified_network=False)
    # vehicle = vsp_read(r"C:\Users\OHAGANLU\SUAVE\Tutorials-2.5.2\ATR_72-600\ATR72-600_tcd_pc.vsp3", units_type='SI', specified_network=False)
    vehicle.tag = 'ATR_72-600'  

    if hasattr(vehicle, 'wings'):

        if 'wing' in vehicle.wings:
            wing_vsp = vehicle.wings.pop('wing')
            wing_vsp.tag = 'main_wing'
            vehicle.wings['main_wing'] = wing_vsp

        if 'htail' in vehicle.wings:
            htail_vsp = vehicle.wings.pop('htail')
            htail_vsp.tag = 'horizontal_stabilizer'
            vehicle.wings['horizontal_stabilizer'] = htail_vsp

        if 'vtail' in vehicle.wings:
            vtail_vsp = vehicle.wings.pop('vtail')
            vtail_vsp.tag = 'vertical_stabilizer'
            vehicle.wings['vertical_stabilizer'] = vtail_vsp

    print("Wings renamed to:", list(vehicle.wings.keys()))

    vehicle.mass_properties.max_takeoff               = 22800 * Units.kilogram 
    vehicle.mass_properties.takeoff                   = TOW * Units.kilogram   
    vehicle.mass_properties.operating_empty           = 13010 * Units.kilogram 
    vehicle.mass_properties.max_zero_fuel             = 20800 * Units.kilogram
    vehicle.mass_properties.cargo                     = 7550.  * Units.kilogram
    vehicle.envelope.ultimate_load = 3.75
    vehicle.envelope.limit_load    = 2.5
    vehicle.systems.control        = "fully powered" 
    vehicle.systems.accessories    = "medium range"
    vehicle.reference_area = vehicle.wings['main_wing'].areas.reference
    
    wing_vsp = vehicle.wings.main_wing
    wing_vsp.vertical = False
    wing_vsp.symmetric = True
    wing_vsp.high_lift = True
    wing_vsp.dynamic_pressure_ratio = 1.0
    
    htail_vsp = vehicle.wings.horizontal_stabilizer
    htail_vsp.vertical = False
    htail_vsp.symmetric = True
    htail_vsp.dynamic_pressure_ratio = 0.9
    
    vtail_vsp = vehicle.wings.vertical_stabilizer
    vtail_vsp.vertical = True
    vtail_vsp.symmetric = False
    vtail_vsp.t_tail = True
    vtail_vsp.dynamic_pressure_ratio = 1.0

    flap                       = SUAVE.Components.Wings.Control_Surfaces.Flap() 
    flap.tag                   = 'flap' 
    flap.span_fraction_start   = 0.22 
    flap.span_fraction_end     = 0.7611
    flap.deflection            = 0.0 * Units.degrees
    flap.configuration_type    = 'double_slotted'
    flap.chord_fraction        = 0.146
    wing_vsp.append_control_surface(flap)   
            
    aileron                       = SUAVE.Components.Wings.Control_Surfaces.Aileron() 
    aileron.tag                   = 'aileron' 
    aileron.span_fraction_start   = 0.761 
    aileron.span_fraction_end     = 1
    aileron.deflection            = 0.0 * Units.degrees
    aileron.chord_fraction        = 0.238 
    wing_vsp.append_control_surface(aileron)    
      
    fuse_vsp = vehicle.fuselages.fuselage_1
    fuse_vsp.tag = 'fuselage'
    
    fuse_vsp.number_coach_seats = 72
    fuse_vsp.seats_abreast = 4
    fuse_vsp.seat_pitch = 1.0 * Units.meter
    fuse_vsp.areas.side_projected = fuse_vsp.lengths.total * fuse_vsp.width
    fuse_vsp.differential_pressure = 5.0e4 * Units.pascal

    nacelle1 = Nacelle()
    nacelle1.tag = 'nacelle1'
    nacelle1.length = 2.13 * Units.meter
    nacelle1.diameter = 0.72* Units.meter
    nacelle1.inlet_diameter = 0.72 * Units.meter
    nacelle1.area = 3.14 * (nacelle1.diameter / 2)**2
    nacelle1.origin = [[8.42146 * Units.meter, 4.104 * Units.meter, 1.014 * Units.meter]]

    vehicle.append_component(nacelle1)

    nacelle2 = Nacelle()
    nacelle2.tag = 'nacelle2'
    nacelle2.length = 2.13* Units.meter
    nacelle2.diameter = 0.72 * Units.meter
    nacelle2.inlet_diameter = 0.72 * Units.meter
    nacelle2.area = 3.14 * (nacelle2.diameter / 2)**2
    nacelle2.origin = [[8.42146 * Units.meter, -4.104 * Units.meter, 1.014 * Units.meter]]

    vehicle.append_component(nacelle2)

    turbofan = SUAVE.Components.Energy.Networks.Turbofan()

    turbofan.tag = 'turbofan'

    turbofan.number_of_engines = 2
    turbofan.bypass_ratio      = 5.4
    turbofan.origin            = [[8.42146, 4.104, 1.014],[8.42146, -4.104, 1.104]] * Units.meter

    turbofan.working_fluid = SUAVE.Attributes.Gases.Air()

    ram = SUAVE.Components.Energy.Converters.Ram()
    ram.tag = 'ram'
    
    turbofan.append(ram)

    inlet_nozzle = SUAVE.Components.Energy.Converters.Compression_Nozzle()
    inlet_nozzle.tag = 'inlet_nozzle'

    inlet_nozzle.polytropic_efficiency = 0.98
    inlet_nozzle.pressure_ratio        = 0.98

    turbofan.append(inlet_nozzle)
    
    compressor = SUAVE.Components.Energy.Converters.Compressor()    
    compressor.tag = 'low_pressure_compressor'

    compressor.polytropic_efficiency = 0.91
    compressor.pressure_ratio        = 1.14    

    turbofan.append(compressor)
    
    compressor = SUAVE.Components.Energy.Converters.Compressor()    
    compressor.tag = 'high_pressure_compressor'

    compressor.polytropic_efficiency = 0.91
    compressor.pressure_ratio        = 13.415    

    turbofan.append(compressor)

    turbine = SUAVE.Components.Energy.Converters.Turbine()   
    turbine.tag='low_pressure_turbine'
    
    turbine.mechanical_efficiency = 0.99
    turbine.polytropic_efficiency = 0.93     
    
    turbofan.append(turbine)
      
    turbine = SUAVE.Components.Energy.Converters.Turbine()   
    turbine.tag='high_pressure_turbine'

    turbine.mechanical_efficiency = 0.99
    turbine.polytropic_efficiency = 0.93     

    turbofan.append(turbine)  
       
    combustor = SUAVE.Components.Energy.Converters.Combustor()   
    combustor.tag = 'combustor'
    
    combustor.efficiency                = 0.99 
    combustor.alphac                    = 1.0   
    combustor.turbine_inlet_temperature = 1450 # K
    combustor.pressure_ratio            = 0.95
    combustor.fuel_data                 = SUAVE.Attributes.Propellants.Jet_A()    
    
    turbofan.append(combustor)

    nozzle = SUAVE.Components.Energy.Converters.Expansion_Nozzle()   
    nozzle.tag = 'core_nozzle'
 
    nozzle.polytropic_efficiency = 0.95
    nozzle.pressure_ratio        = 0.99    

    turbofan.append(nozzle)

    nozzle = SUAVE.Components.Energy.Converters.Expansion_Nozzle()   
    nozzle.tag = 'fan_nozzle'

    nozzle.polytropic_efficiency = 0.95
    nozzle.pressure_ratio        = 0.99    

    turbofan.append(nozzle)
    
    fan = SUAVE.Components.Energy.Converters.Fan()   
    fan.tag = 'fan'

    fan.polytropic_efficiency = 0.93
    fan.pressure_ratio        = 1.7    

    turbofan.append(fan)
    
    thrust = SUAVE.Components.Energy.Processes.Thrust()       
    thrust.tag ='compute_thrust'
 
    thrust.total_design             = 2*12000. * Units.N
    
    turbofan.thrust = thrust
    
    altitude      = 15000.0*Units.ft
    mach_number   = 0.55  

    turbofan_sizing(turbofan,mach_number,altitude)   

    vehicle.append_component(turbofan)    
    
    plot_vehicle(vehicle)

    return vehicle

def configs_setup(vehicle):

    configs = SUAVE.Components.Configs.Config.Container()

    base_config = SUAVE.Components.Configs.Config(vehicle)
    base_config.tag = 'base'
    configs.append(base_config)

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'cruise'
    configs.append(config)

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'takeoff'
    config.wings['main_wing'].control_surfaces.flap.deflection = 0. * Units.deg
    config.max_lift_coefficient_factor    = 1.

    configs.append(config)

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'cutback'
    config.wings['main_wing'].control_surfaces.flap.deflection = 15. * Units.deg
    config.max_lift_coefficient_factor    = 1.

    configs.append(config)    

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'approach'
    config.wings['main_wing'].control_surfaces.flap.deflection = 15. * Units.deg
    config.max_lift_coefficient_factor    = 1.

    configs.append(config)  

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'final_approach'
    config.wings['main_wing'].control_surfaces.flap.deflection = 30. * Units.deg
    config.max_lift_coefficient_factor    = 1.
    configs.append(config)

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'short_field_takeoff'
    config.wings['main_wing'].control_surfaces.flap.deflection = 15. * Units.deg
    config.max_lift_coefficient_factor    = 1. 
  
    configs.append(config)

    return configs

def simple_sizing(configs):

    base = configs.base
    base.pull_base()

    for wing in base.wings:
        wing.areas.wetted   = 2.0 * wing.areas.reference
        wing.areas.exposed  = 0.8 * wing.areas.wetted
        wing.areas.affected = 0.6 * wing.areas.wetted

    base.store_diff()

    return

def mission_setup(analyses, AC_reg, Flight_No):

    mission = SUAVE.Analyses.Mission.Sequential_Segments()
    mission.tag = 'the_mission'

    print("\n",AC_reg)
    print(Flight_No,"\n")

    # climb_file = '/Users/OHAGANLU/OneDrive - Trinity College Dublin/Opensky_Flights/Mission Segment Data/{}/climb_segments.csv'.format(Flight_No)
    climb_file = '/Users/Luke TCD Woek/OneDrive - Trinity College Dublin/Opensky_Flights/Mission Segment Data/{}/climb_segments.csv'.format(Flight_No)

    with open(climb_file, 'r') as file:
        climb_segments = np.loadtxt(file, delimiter=",")

    airport = SUAVE.Attributes.Airports.Airport()
    airport.altitude   =  0.0  * Units.ft
    airport.delta_isa  =  0.0
    airport.atmosphere = SUAVE.Attributes.Atmospheres.Earth.US_Standard_1976()

    mission.airport = airport    

    Segments = SUAVE.Analyses.Mission.Segments

    base_segment = Segments.Segment()
    base_segment.state.numerics.number_control_points = 8

    # ------------------------------------------------------------------
    #   First Climb Segment: Linear Speed, Constant Rate
    # ------------------------------------------------------------------
    
    for i in range(len(climb_segments[0])):
        
        segment = Segments.Climb.Linear_Speed_Constant_Rate(base_segment) 
        segment.tag = "climb_%d" % (i+1)
        ones_row = segment.state.ones_row
        
        if i == 0:
            segment.analyses.extend( analyses.takeoff )
            analyses.takeoff.aerodynamics.settings.spoiler_drag_increment = 0.0198 
            segment.state.unknowns.body_angle = ones_row(1) * 5 * Units.degrees
        else:
            segment.analyses.extend( analyses.cruise )

        segment.altitude_start  = climb_segments[0,i]  * Units.m
        segment.altitude_end    = climb_segments[1,i]  * Units.m
        segment.air_speed_start = climb_segments[2,i] * Units['m/s']
        segment.air_speed_end   = climb_segments[3,i] * Units['m/s']
        segment.climb_rate      = climb_segments[4,i] * Units['m/s']
        
        segment.state.unknowns.body_angle = ones_row(1) * climb_segments[5,i] * Units.degrees
        segment.state.unknowns.throttle = ones_row(1) * 0.8

        # Add to misison
        mission.append_segment(segment)

        

     # ------------------------------------------------------------------    
    #   Cruise Segment: Constant Speed, Constant Altitude
    # ------------------------------------------------------------------    

    # cruise_file = '/Users/OHAGANLU/OneDrive - Trinity College Dublin/Opensky_Flights/Mission Segment Data/{}/cruise_segments.csv'.format(Flight_No)
    cruise_file = '/Users/Luke TCD Woek/OneDrive - Trinity College Dublin/Opensky_Flights/Mission Segment Data/{}/cruise_segments.csv'.format(Flight_No)

    with open(cruise_file, 'r') as file1:
        cruise_segments = np.loadtxt(file1, delimiter=",")
        
    segment = Segments.Cruise.Constant_Speed_Constant_Altitude_Loiter(base_segment)
    segment.tag = "cruise_1"
    ones_row = segment.state.ones_row

    segment.analyses.extend( analyses.cruise )

    segment.altitude  = cruise_segments[0]  * Units.m
    segment.air_speed = cruise_segments[1] * Units['m/s']
    segment.time      = cruise_segments[2] * Units.min
    segment.state.numerics.number_control_points = 16
    
    segment.state.unknowns.throttle = 0.75 * ones_row(1)
    
    # Add to misison
    mission.append_segment(segment)

    # descent_file = '/Users/OHAGANLU/OneDrive - Trinity College Dublin/Opensky_Flights/Mission Segment Data/{}/descent_segments.csv'.format(Flight_No)
    descent_file = '/Users/Luke TCD Woek/OneDrive - Trinity College Dublin/Opensky_Flights/Mission Segment Data/{}/descent_segments.csv'.format(Flight_No)
    
    with open(descent_file, 'r') as file2:
        descent_segments = np.genfromtxt(file2, delimiter=",")
        
    for k in range(len(descent_segments[0])):
        
        segment = Segments.Descent.Linear_Mach_Constant_Rate(base_segment)
        segment.tag = "descent_%d" % (k+1)
        ones_row = segment.state.ones_row
        
        if k == (len(descent_segments[0]) - 1):
            segment.analyses.extend( analyses.final_approach )
            analyses.final_approach.aerodynamics.settings.spoiler_drag_increment = 0.05
            segment.state.unknowns.body_angle = ones_row(1) * 6.0 * Units.degrees
        elif k == (len(descent_segments[0]) - 2):
            segment.analyses.extend( analyses.approach )
            analyses.approach.aerodynamics.settings.spoiler_drag_increment = 0.015
            segment.state.unknowns.body_angle = ones_row(1) * 2.0 * Units.degrees
        else:
            segment.analyses.extend( analyses.cruise )

        segment.altitude_start  = descent_segments[0,k]  * Units.m
        segment.altitude_end    = descent_segments[1,k]  * Units.m
        segment.air_speed_start = descent_segments[2,k] * Units['m/s']
        segment.air_speed_end   = descent_segments[3,k] * Units['m/s']
        segment.descent_rate    = descent_segments[4,k] * Units['m/s']
        
        segment.state.unknowns.throttle = 0.125 * ones_row(1)
        segment.state.unknowns.body_angle = ones_row(1) * descent_segments[5,k] * Units.degrees

        # Add to misison
        mission.append_segment(segment)

    return mission

def missions_setup(base_mission):

    missions = SUAVE.Analyses.Mission.Mission.Container()

    missions.base = base_mission

    return missions 

def plot_fuel_flow(results, Flight_No, TOW, line_color='bo-', save_figure=False,
                   save_filename="Fuel_Flow", file_type=".png"):
    axis_font = {'size': '14'} 
    fig = plt.figure(save_filename)
    fig.set_size_inches(10, 8)

    # === Base directory for mission results ===
    # base_dir = f'/Users/OHAGANLU/OneDrive - Trinity College Dublin/SUAVE/SUAVE_mission_results/{Flight_No}'
    base_dir = f'/Users/Luke TCD Woek/OneDrive - Trinity College Dublin/SUAVE/SUAVE_mission_results/{Flight_No}'
    os.makedirs(base_dir, exist_ok=True)  # ✅ create the folder for this flight

    # === Define filenames ===
    mdot_filename     = os.path.join(base_dir, '_mdot.csv')
    time_filename     = os.path.join(base_dir, '_time.csv')
    fuel_filename     = os.path.join(base_dir, '_fuel.csv')
    pitch_filename    = os.path.join(base_dir, '_pitch.csv')
    throttle_filename = os.path.join(base_dir, '_throttle.csv')

    # === Clear old data (overwrite if exists) ===
    for filename in [mdot_filename, time_filename, fuel_filename, pitch_filename, throttle_filename]:
        open(filename, 'w').close()  # creates or empties file safely

    # === Loop through all segments ===
    for segment in results.segments.values(): 
        time       = segment.conditions.frames.inertial.time[:, 0] / Units.min
        mass       = segment.conditions.weights.total_mass[:, 0] / Units.kg
        mdot       = segment.conditions.weights.vehicle_mass_rate[:, 0] / Units['kg/hr']
        fuel_burn  = TOW - mass
        body_angle = segment.conditions.frames.body.inertial_rotations[:, 1, None] / Units.degrees
        throttle   = segment.conditions.propulsion.throttle[:, 0]

        # === Plot ===
        axes = plt.subplot(2, 1, 1)
        axes.plot(time, mdot, line_color)
        axes.set_ylabel('Fuel Flow Rate (kg/hr)', axis_font)
        axes.set_xlabel('Time (mins)', axis_font)
        set_axes(axes)

        axes = plt.subplot(2, 1, 2)
        axes.plot(time, fuel_burn, line_color)
        axes.set_ylabel('Fuel Burn (kg)', axis_font)
        axes.set_xlabel('Time (mins)', axis_font)
        set_axes(axes)

        # === Save data to files ===
        for filename, data in [
            (mdot_filename, mdot),
            (time_filename, time),
            (fuel_filename, fuel_burn),
            (pitch_filename, body_angle),
            (throttle_filename, throttle)
        ]:
            try:
                with open(filename, 'a') as file:
                    np.savetxt(file, np.atleast_1d(data), delimiter=' ')
            except PermissionError:
                print(f"⚠️ Permission denied for {filename}. "
                      "Check if it's open or locked by OneDrive/Excel.")
            except Exception as e:
                print(f"❌ Error writing to {filename}: {e}")

    # === Save figure ===
    if save_figure:
        fig_path = os.path.join(base_dir, f"{save_filename}{file_type}")
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        print(f"✅ Figure saved to {fig_path}")

    return

def plot_mission(results, AC_reg, Flight_No, TOW, line_style='bo-'):

    plot_flight_conditions(results, line_style)

    plot_aerodynamic_forces(results, line_style)

    plot_aerodynamic_coefficients(results, line_style)

    plot_drag_components(results, line_style)

    plot_altitude_sfc_weight(results, line_style)

    plot_aircraft_velocities(results, line_style) 

    # plot_fuel_flow(results, Flight_No, TOW, line_style)
        
    return

if __name__ == '__main__': 

    main()
    

    plt.show()

