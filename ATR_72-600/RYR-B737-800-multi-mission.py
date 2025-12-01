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
import matplotlib.pyplot as plt
import time
import os
# SUAVE Imports
import SUAVE
assert SUAVE.__version__=='2.5.2', 'These tutorials only work with the SUAVE 2.5.2 release'
from SUAVE.Core import Data, Units 
from SUAVE.Plots.Performance.Mission_Plots import *
from copy import deepcopy
import joblib
from SUAVE.Plots.Geometry import plot_vehicle
# ----------------------------------------------------------------------
#   Main
# ----------------------------------------------------------------------

def main():
    """This function gets the vehicle configuration, analysis settings, and then runs the mission.
    Once the mission is complete, the results are plotted."""
    
    startTime = time.time()
    
    with open('/Users/lukeohagan/Library/CloudStorage/OneDrive-TrinityCollegeDublin/5th-Year/Research-Project/mySUAVE/RyanairFlightsAC.txt', 'r') as file:
        RyanairFlightsAC = np.genfromtxt(file, dtype='str')
        print(RyanairFlightsAC)
    
    with open('/Users/lukeohagan/Library/CloudStorage/OneDrive-TrinityCollegeDublin/5th-Year/Research-Project/mySUAVE/RyanairFlightsFN.txt', 'r') as file:
        RyanairFlightsFN = np.genfromtxt(file, dtype='str')
        print(RyanairFlightsFN)
    
    with open('/Users/lukeohagan/Library/CloudStorage/OneDrive-TrinityCollegeDublin/5th-Year/Research-Project/mySUAVE/RyanairFlightsTOW.txt', 'r') as file:
        RyanairFlightsTOW = np.loadtxt(file)
        print(RyanairFlightsTOW)
    
    AC_reg = RyanairFlightsAC[0]
    Flight_No = RyanairFlightsFN[0]
    TOW = RyanairFlightsTOW[0]
    
    # Extract vehicle configurations and the analysis settings that go with them
    vehicle, configs = full_setup_1(TOW)
        
    for i in range(len(RyanairFlightsAC)):
        
        AC_reg = RyanairFlightsAC[i]
        Flight_No = RyanairFlightsFN[i]
        TOW = RyanairFlightsTOW[i]
      
        vehicle, analyses = full_setup_2(vehicle, configs, AC_reg, Flight_No, TOW)
        
        # Size each of the configurations according to a given set of geometry relations
        simple_sizing(configs)

        # Perform operations needed to make the configurations and analyses usable in the mission
        configs.finalize()
        analyses.finalize()

        # Determine the vehicle weight breakdown (independent of mission fuel usage)
# =============================================================================
#         weights = analyses.configs.base.weights
#         breakdown = weights.evaluate()
# =============================================================================

        # Perform a mission analysis
       
        mission = analyses.missions.base
       
        results = mission.evaluate()
           
        # Plot all mission results, including items such as altitude profile and L/D
        plot_mission(results, AC_reg, Flight_No, TOW)
       
    endTime = time.time()
    
    print((endTime-startTime)/60)
    
    return

# ----------------------------------------------------------------------
#   Analysis Setup
# ----------------------------------------------------------------------

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

# ----------------------------------------------------------------------
#   Define the Vehicle Analyses
# ----------------------------------------------------------------------

def analyses_setup(configs):
    """Set up analyses for each of the different configurations."""
    
    analyses = SUAVE.Analyses.Analysis.Container()

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

def vehicle_setup(TOW):
    """This is the full physical definition of the vehicle, and is designed to be independent of the
    analyses that are selected."""
    
    # ------------------------------------------------------------------
    #   Initialize the Vehicle
    # ------------------------------------------------------------------    
    
    vehicle = SUAVE.Vehicle()
    vehicle.tag = 'Boeing_737-800'    
    
    # ------------------------------------------------------------------
    #   Vehicle-level Properties
    # ------------------------------------------------------------------    

    vehicle.mass_properties.max_takeoff               = 79016.0 * Units.kilogram 
    vehicle.mass_properties.takeoff                   = TOW     * Units.kilogram   
    vehicle.mass_properties.operating_empty           = 41413.0 * Units.kilogram 
    vehicle.mass_properties.max_zero_fuel             = 62732.0 * Units.kilogram
    vehicle.mass_properties.cargo                     = 10000.  * Units.kilogram   
    
    # Envelope properties
    vehicle.envelope.ultimate_load = 3.75
    vehicle.envelope.limit_load    = 2.5

    # Vehicle level parameters
    vehicle.reference_area         = 130.21 * Units['meters**2']  
    vehicle.passengers             = 184
    vehicle.systems.control        = "fully powered" 
    vehicle.systems.accessories    = "medium range"

    # ------------------------------------------------------------------        
    #  Landing Gear
    # ------------------------------------------------------------------ 

    landing_gear = SUAVE.Components.Landing_Gear.Landing_Gear()
    landing_gear.tag = "main_landing_gear"
    
    landing_gear.main_tire_diameter = 1.12000 * Units.m
    landing_gear.nose_tire_diameter = 0.6858 * Units.m
    landing_gear.main_strut_length  = 1.8 * Units.m
    landing_gear.nose_strut_length  = 1.3 * Units.m
    landing_gear.main_units  = 2    # Number of main landing gear
    landing_gear.nose_units  = 1    # Number of nose landing gear
    landing_gear.main_wheels = 2    # Number of wheels on the main landing gear
    landing_gear.nose_wheels = 2    # Number of wheels on the nose landing gear      
    vehicle.landing_gear = landing_gear

    # ------------------------------------------------------------------        
    #   Main Wing
    # ------------------------------------------------------------------        
    
    wing = SUAVE.Components.Wings.Main_Wing()
    wing.tag = 'main_wing'
    
    wing.aspect_ratio            = 9.84
    wing.sweeps.quarter_chord    = 25 * Units.deg
    wing.thickness_to_chord      = 0.1
    wing.taper                   = 0.1
    wing.spans.projected         = 35.79 * Units.meter
    wing.chords.root             = 7.760 * Units.meter
    wing.chords.tip              = 0.782 * Units.meter
    wing.chords.mean_aerodynamic = 4.235 * Units.meter
    wing.areas.reference         = 130.21 * Units['meters**2']  
    wing.twists.root             = 4.0 * Units.degrees
    wing.twists.tip              = 0.0 * Units.degrees
    wing.origin                  = [[13.61, 0, -1.27]] * Units.meter
    wing.vertical                = False
    wing.symmetric               = True
    wing.high_lift               = True
    wing.dynamic_pressure_ratio  = 1.0
    
    # ------------------------------------------------------------------
    #   Main Wing Control Surfaces
    # ------------------------------------------------------------------
    
    flap                       = SUAVE.Components.Wings.Control_Surfaces.Flap() 
    flap.tag                   = 'flap' 
    flap.span_fraction_start   = 0.20 
    flap.span_fraction_end     = 0.70   
    flap.deflection            = 0.0 * Units.degrees
    flap.configuration_type    = 'double_slotted'
    flap.chord_fraction        = 0.30   
    wing.append_control_surface(flap)   
        
    slat                       = SUAVE.Components.Wings.Control_Surfaces.Slat() 
    slat.tag                   = 'slat' 
    slat.span_fraction_start   = 0.324 
    slat.span_fraction_end     = 0.963     
    slat.deflection            = 0.0 * Units.degrees
    slat.chord_fraction        = 0.1  	 
    wing.append_control_surface(slat)  
        
    aileron                       = SUAVE.Components.Wings.Control_Surfaces.Aileron() 
    aileron.tag                   = 'aileron' 
    aileron.span_fraction_start   = 0.7 
    aileron.span_fraction_end     = 0.963 
    aileron.deflection            = 0.0 * Units.degrees
    aileron.chord_fraction        = 0.16    
    wing.append_control_surface(aileron)    
    
    # Add to vehicle
    vehicle.append_component(wing)    

    # ------------------------------------------------------------------        
    #  Horizontal Stabilizer
    # ------------------------------------------------------------------        
    
    wing = SUAVE.Components.Wings.Horizontal_Tail()
    wing.tag = 'horizontal_stabilizer'
    
    wing.aspect_ratio            = 6.16     
    wing.sweeps.quarter_chord    = 40.0 * Units.deg
    wing.thickness_to_chord      = 0.08
    wing.taper                   = 0.2
    wing.spans.projected         = 14.2 * Units.meter
    wing.chords.root             = 4.7  * Units.meter
    wing.chords.tip              = 0.955 * Units.meter
    wing.chords.mean_aerodynamic = 3.0  * Units.meter
    wing.areas.reference         = 32.488   * Units['meters**2']  
    wing.twists.root             = 3.0 * Units.degrees
    wing.twists.tip              = 3.0 * Units.degrees  
    wing.origin                  = [[32.83 * Units.meter, 0 , 1.14 * Units.meter]]
    wing.vertical                = False 
    wing.symmetric               = True
    wing.dynamic_pressure_ratio  = 0.9  
    
    # Add to vehicle
    vehicle.append_component(wing)
    
    # ------------------------------------------------------------------
    #   Vertical Stabilizer
    # ------------------------------------------------------------------
    
    wing = SUAVE.Components.Wings.Vertical_Tail()
    wing.tag = 'vertical_stabilizer'    

    wing.aspect_ratio            = 1.91
    wing.sweeps.quarter_chord    = 25. * Units.deg
    wing.thickness_to_chord      = 0.08
    wing.taper                   = 0.25
    wing.spans.projected         = 7.777 * Units.meter
    wing.chords.root             = 8.19  * Units.meter
    wing.chords.tip              = 0.95  * Units.meter
    wing.chords.mean_aerodynamic = 4.0   * Units.meter
    wing.areas.reference         = 27.316 * Units['meters**2']  
    wing.twists.root             = 0.0 * Units.degrees
    wing.twists.tip              = 0.0 * Units.degrees  
    wing.origin                  = [[28.79 * Units.meter, 0, 1.54 * Units.meter]] # meters
    wing.vertical                = True 
    wing.symmetric               = False
    wing.t_tail                  = False
    wing.dynamic_pressure_ratio  = 1.0
        
    # Add to vehicle
    vehicle.append_component(wing)

    # ------------------------------------------------------------------
    #  Fuselage
    # ------------------------------------------------------------------
    
    fuselage = SUAVE.Components.Fuselages.Fuselage()
    fuselage.tag = 'fuselage'
    
    fuselage.number_coach_seats    = vehicle.passengers
    fuselage.seats_abreast         = 6
    fuselage.seat_pitch            = 0.762     * Units.meter
    fuselage.fineness.nose         = 1.6
    fuselage.fineness.tail         = 2.
    fuselage.lengths.nose          = 6.4   * Units.meter
    fuselage.lengths.tail          = 8.0   * Units.meter
    fuselage.lengths.total         = 38.02 * Units.meter # EDIT WETTED AREA
    fuselage.width                 = 3.76  * Units.meter
    fuselage.heights.maximum       = 3.76  * Units.meter
    fuselage.effective_diameter    = 3.76     * Units.meter
    fuselage.areas.side_projected  = 142.1948 * Units['meters**2'] 
    fuselage.areas.wetted          = 446.718  * Units['meters**2'] 
    fuselage.areas.front_projected = 12.57    * Units['meters**2'] 
    fuselage.differential_pressure = 5.0e4 * Units.pascal
    fuselage.heights.at_quarter_length          = 3.76 * Units.meter
    fuselage.heights.at_three_quarters_length   = 3.65 * Units.meter
    fuselage.heights.at_wing_root_quarter_chord = 3.76 * Units.meter
    
    # add to vehicle
    vehicle.append_component(fuselage)
    
    # ------------------------------------------------------------------
    #   Nacelles
    # ------------------------------------------------------------------ 
    nacelle                       = SUAVE.Components.Nacelles.Nacelle()
    nacelle.tag                   = 'nacelle_1'
    nacelle.length                = 2.508
    nacelle.inlet_diameter        = 1.55
    nacelle.diameter              = 1.98
    nacelle.areas.wetted          = 1.1*np.pi*nacelle.diameter*nacelle.length
    nacelle.origin                = [[13.72, -4.86,-1.9]]
    nacelle.flow_through          = True  
    nacelle_airfoil               = SUAVE.Components.Airfoils.Airfoil() 
    nacelle_airfoil.naca_4_series_airfoil = '2410'
    nacelle.append_airfoil(nacelle_airfoil)

    nacelle_2                     = deepcopy(nacelle)
    nacelle_2.tag                 = 'nacelle_2'
    nacelle_2.origin              = [[13.72, 4.86,-1.9]]
    
    vehicle.append_component(nacelle)  
    vehicle.append_component(nacelle_2)     
        

    # ------------------------------------------------------------------
    #   Turbofan Network
    # ------------------------------------------------------------------
     
    turbofan = SUAVE.Components.Energy.Networks.Propulsor_Surrogate()

    turbofan.tag = 'turbofan'
    turbofan.number_of_engines = 1
    turbofan.origin            = [[13.72, 4.86,-1.9],[13.72, -4.86,-1.9]] * Units.meter
    turbofan.use_extended_surrogate = False
   
    check_sfc = os.path.isfile('/Users/lukeohagan/SUAVE/SUAVE/mySUAVE/SurrogatePathFile/sfc_surrogate.pkl')
    check_thr = os.path.isfile('/Users/lukeohagan/SUAVE/SUAVE/mySUAVE/SurrogatePathFile/thr_surrogate.pkl')

    if check_sfc is True and check_thr is True:
        print("Loading Surrogate Model...")
        turbofan.sfc_surrogate = joblib.load('/Users/lukeohagan/SUAVE/SUAVE/mySUAVE/SurrogatePathFile/sfc_surrogate.pkl')
        turbofan.thrust_surrogate = joblib.load('/Users/lukeohagan/SUAVE/SUAVE/mySUAVE/SurrogatePathFile/thr_surrogate.pkl')
        turbofan.altitude_input_scale = 12801.6
        turbofan.sfc_input_scale = 0.000176924
        turbofan.thrust_input_scale = 246661.0057
        turbofan.thrust_anchor_scale = 1.0000
       
    else:
        print("Building Surrogate Model...")
        #turbofan.input_file = '/Users/lukeohagan/Library/CloudStorage/OneDrive-TrinityCollegeDublin/5th-Year/Research-Project/mySUAVE/CFM56-7B26_Engine_Deck_PHE/CFM56-7B26-COMBINED-PHE-BASELINE-ENGINE-DECK.csv'
        turbofan.input_file = '/Users/lukeohagan/SUAVE/SUAVE/mySUAVE/CFM56-7B26-Engine-Deck/EngineDeck-CFM56-7B26-3-sorted.csv'
        turbofan.build_surrogate()
 
        
    # Add turbofan network to the vehicle 
    vehicle.append_component(turbofan)      

    # ------------------------------------------------------------------
    #   Vehicle Definition Complete
    # ------------------------------------------------------------------
    
    plot_vehicle(vehicle, axis_limits=15)
    
   
    
    return vehicle



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
    config.wings['main_wing'].control_surfaces.flap.deflection = 5. * Units.deg
    config.wings['main_wing'].control_surfaces.slat.deflection = 5. * Units.deg
    config.max_lift_coefficient_factor    = 1.

    configs.append(config)
    
    # ------------------------------------------------------------------
    #   Cutback Configuration
    # ------------------------------------------------------------------
    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'cutback'
    config.wings['main_wing'].control_surfaces.flap.deflection = 5. * Units.deg
    config.wings['main_wing'].control_surfaces.slat.deflection = 5. * Units.deg
    config.max_lift_coefficient_factor    = 1.

    configs.append(config)    

    # ------------------------------------------------------------------
    #   Landing Configuration
    # ------------------------------------------------------------------

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'approach'
    config.wings['main_wing'].control_surfaces.flap.deflection = 30. * Units.deg
    config.wings['main_wing'].control_surfaces.slat.deflection = 30. * Units.deg  
    config.max_lift_coefficient_factor    = 1.

    configs.append(config)
    
    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'final_approach'
    config.wings['main_wing'].control_surfaces.flap.deflection = 30. * Units.deg
    config.wings['main_wing'].control_surfaces.slat.deflection = 30. * Units.deg  
    config.max_lift_coefficient_factor    = 1.

    configs.append(config)

    # ------------------------------------------------------------------
    #   Short Field Takeoff Configuration
    # ------------------------------------------------------------------ 

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'short_field_takeoff'
    config.wings['main_wing'].control_surfaces.flap.deflection = 20. * Units.deg
    config.wings['main_wing'].control_surfaces.slat.deflection = 20. * Units.deg
    config.max_lift_coefficient_factor    = 1. 
  
    configs.append(config)

    return configs

def simple_sizing(configs):
    """This function applies a few basic geometric sizing relations and modifies the landing
    configuration."""

    base = configs.base
    base.pull_base()
    # base.mass_properties.max_zero_fuel = 0.9 * base.mass_properties.max_takeoff 

    # Estimate wing areas
    for wing in base.wings:
        wing.areas.wetted   = 2.0 * wing.areas.reference
        wing.areas.exposed  = 0.8 * wing.areas.wetted
        wing.areas.affected = 0.6 * wing.areas.wetted

    base.store_diff()

    # ------------------------------------------------------------------
    #   Landing Configuration
    # ------------------------------------------------------------------
    # landing = configs.landing
    # landing.pull_base()
    # landing.mass_properties.landing = 0.85 * base.mass_properties.takeoff
    # landing.store_diff()

    return

# ----------------------------------------------------------------------
#   Define the Mission
# ----------------------------------------------------------------------

def mission_setup(analyses, AC_reg, Flight_No):
    """This function defines the baseline mission that will be flown by the aircraft in order
    to compute performance."""

    # ------------------------------------------------------------------
    #   Initialize the Mission
    # ------------------------------------------------------------------

    mission = SUAVE.Analyses.Mission.Sequential_Segments()
    mission.tag = 'the_mission'
    
    print("\n",AC_reg)
    print(Flight_No,"\n")
    
    # climb_file = '%s\%s\Segments\%s_climb_segments.csv' % (AC_reg, Flight_No, Flight_No)
    
    
    
    climb_file = '/Users/lukeohagan/Library/CloudStorage/OneDrive-TrinityCollegeDublin/5th-Year/Research-Project/mySUAVE/Results/{}/{}/{}_climb_segments.csv'.format(AC_reg, Flight_No, Flight_No)
    
    with open(climb_file, 'r') as file:
        climb_segments = np.loadtxt(file, delimiter=",")

    # Airport
    airport = SUAVE.Attributes.Airports.Airport()
    airport.altitude   =  climb_segments[0,0]  * Units.m
    airport.delta_isa  =  0.0
    airport.atmosphere = SUAVE.Attributes.Atmospheres.Earth.US_Standard_1976()

    mission.airport = airport    

    # Unpack Segments module
    Segments = SUAVE.Analyses.Mission.Segments

    # Base segment 
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
            segment.state.unknowns.body_angle = ones_row(1) * 10 * Units.degrees
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

    cruise_file = '/Users/lukeohagan/Library/CloudStorage/OneDrive-TrinityCollegeDublin/5th-Year/Research-Project/mySUAVE/Results/{}/{}/{}_cruise_segments.csv'.format(AC_reg, Flight_No, Flight_No)
    
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

    # ------------------------------------------------------------------
    #   First Descent Segment: Constant Speed, Constant Rate
    # ------------------------------------------------------------------
    
    # ------------------------------------------------------------------
    #   First Descent Segment: Constant Speed, Constant Rate
    # ------------------------------------------------------------------

# =============================================================================
#     segment = Segments.Descent.Constant_Speed_Constant_Rate(base_segment)
#     segment.tag = "descent_1"
# 
#     segment.analyses.extend( analyses.cruise )
# 
#     segment.altitude_end = 8.0   * Units.km
#     segment.air_speed    = 220.0 * Units['m/s']
#     segment.descent_rate = 4.5   * Units['m/s']
# 
#     # Add to mission
#     mission.append_segment(segment)
# 
#     # ------------------------------------------------------------------
#     #   Second Descent Segment: Constant Speed, Constant Rate
#     # ------------------------------------------------------------------
# 
#     segment = Segments.Descent.Constant_Speed_Constant_Rate(base_segment)
#     segment.tag = "descent_2"
# 
#     segment.analyses.extend( analyses.final_approach )
# 
#     segment.altitude_end = 6.0   * Units.km
#     segment.air_speed    = 195.0 * Units['m/s']
#     segment.descent_rate = 5.0   * Units['m/s']
# 
#     # Add to mission
#     mission.append_segment(segment)
# 
#     # ------------------------------------------------------------------
#     #   Third Descent Segment: Constant Speed, Constant Rate
#     # ------------------------------------------------------------------
# 
#     segment = Segments.Descent.Constant_Speed_Constant_Rate(base_segment)
#     segment.tag = "descent_3"
# 
#     segment.analyses.extend( analyses.final_approach )
#     # While it is set to zero here and therefore unchanged, a drag increment can be used if
#     # desired. This can avoid negative throttle values if drag generated by the base airframe
#     # is insufficient for the desired descent speed and rate.
#     analyses.final_approach.aerodynamics.settings.spoiler_drag_increment = 0.00
# 
#     segment.altitude_end = 4.0   * Units.km
#     segment.air_speed    = 170.0 * Units['m/s']
#     segment.descent_rate = 5.0   * Units['m/s']
# 
#     # Add to mission
#     mission.append_segment(segment)
# 
#     # ------------------------------------------------------------------
#     #   Fourth Descent Segment: Constant Speed, Constant Rate
#     # ------------------------------------------------------------------
# 
#     segment = Segments.Descent.Constant_Speed_Constant_Rate(base_segment)
#     segment.tag = "descent_4"
# 
#     segment.analyses.extend( analyses.final_approach )
#     analyses.final_approach.aerodynamics.settings.spoiler_drag_increment = 0.00
# 
#     segment.altitude_end = 2.0   * Units.km
#     segment.air_speed    = 150.0 * Units['m/s']
#     segment.descent_rate = 5.0   * Units['m/s']
# 
#     # Add to mission
#     mission.append_segment(segment)
# 
#     # ------------------------------------------------------------------
#     #   Fifth Descent Segment: Constant Speed, Constant Rate
#     # ------------------------------------------------------------------
# 
#     segment = Segments.Descent.Constant_Speed_Constant_Rate(base_segment)
#     segment.tag = "descent_5"
# 
#     segment.analyses.extend( analyses.final_approach )
#     analyses.final_approach.aerodynamics.settings.spoiler_drag_increment = 0.00
# 
#     segment.altitude_end = 0.0   * Units.km
#     segment.air_speed    = 145.0 * Units['m/s']
#     segment.descent_rate = 3.0   * Units['m/s']
# 
#     # Append to mission
#     mission.append_segment(segment)
# =============================================================================


#=============================================================================
    descent_file = '/Users/lukeohagan/Library/CloudStorage/OneDrive-TrinityCollegeDublin/5th-Year/Research-Project/mySUAVE/Results/{}/{}/{}_descent_segments.csv'.format(AC_reg, Flight_No, Flight_No)
    
    with open(descent_file, 'r') as file2:
        descent_segments = np.genfromtxt(file2, delimiter=",")
        
    for k in range(len(descent_segments[0])):
        
        segment = Segments.Descent.Linear_Speed_Constant_Rate(base_segment) # need folder for this \SUAVE\trunk\SUAVE\Methods\Missions\Segments\Descent
        segment.tag = "descent_%d" % (k+1)
        ones_row = segment.state.ones_row
        
        if k == (len(descent_segments[0]) - 1):
            segment.analyses.extend( analyses.final_approach )
            analyses.final_approach.aerodynamics.settings.spoiler_drag_increment = 0.0569
            segment.state.unknowns.body_angle = ones_row(1) * 6.0 * Units.degrees
        elif k == (len(descent_segments[0]) - 2):
            segment.analyses.extend( analyses.approach )
            analyses.approach.aerodynamics.settings.spoiler_drag_increment = 0.0175
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
#=============================================================================
            
    # ------------------------------------------------------------------
    #   Mission definition complete    
    # ------------------------------------------------------------------
    
    return mission

def missions_setup(base_mission):
    """This allows multiple missions to be incorporated if desired, but only one is used here."""

    missions = SUAVE.Analyses.Mission.Mission.Container()

    # ------------------------------------------------------------------
    #   Base Mission
    # ------------------------------------------------------------------

    missions.base = base_mission
    
    return missions  

# ----------------------------------------------------------------------
#   Plot Mission
# ----------------------------------------------------------------------

def plot_mission(results, AC_reg, Flight_No, TOW, line_style='bo-'):
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

    # Plot Fuel Flow - My Function
    plot_fuel_flow(results, AC_reg, Flight_No, TOW, line_style)  
    

        
    return

def plot_fuel_flow(results, AC_reg, Flight_No, TOW, line_color='bo-', save_figure = False, save_filename = "Fuel_Flow", file_type = ".png"):
    axis_font = {'size':'14'} 
    fig = plt.figure(save_filename)
    fig.set_size_inches(10, 8)
    
    
    
    mdot_filename     = '/Users/lukeohagan/Library/CloudStorage/OneDrive-TrinityCollegeDublin/5th-Year/Research-Project/mySUAVE/Results/{}/{}/{}_mdot.csv'.format(AC_reg, Flight_No, Flight_No)
    time_filename     = '/Users/lukeohagan/Library/CloudStorage/OneDrive-TrinityCollegeDublin/5th-Year/Research-Project/mySUAVE/Results/{}/{}/{}_time.csv'.format(AC_reg, Flight_No, Flight_No)
    fuel_filename     = '/Users/lukeohagan/Library/CloudStorage/OneDrive-TrinityCollegeDublin/5th-Year/Research-Project/mySUAVE/Results/{}/{}/{}_fuel.csv'.format(AC_reg, Flight_No, Flight_No)
    pitch_filename    = '/Users/lukeohagan/Library/CloudStorage/OneDrive-TrinityCollegeDublin/5th-Year/Research-Project/mySUAVE/Results/{}/{}/{}_pitch.csv'.format(AC_reg, Flight_No, Flight_No)
    throttle_filename = '/Users/lukeohagan/Library/CloudStorage/OneDrive-TrinityCollegeDublin/5th-Year/Research-Project/mySUAVE/Results/{}/{}/{}_throttle.csv'.format(AC_reg, Flight_No, Flight_No)
    
    with open(mdot_filename, 'w') as file:
        pass #will delete previous
    
    with open(time_filename, 'w') as file:
        pass
        
    with open(fuel_filename, 'w') as file:
        pass
    
    with open(pitch_filename, 'w') as file:
        pass
    
    with open(throttle_filename, 'w') as file:
        pass
        
    for segment in results.segments.values(): 
        time       = segment.conditions.frames.inertial.time[:,0] / Units.min
        mass       = segment.conditions.weights.total_mass[:,0] / Units.kg
        mdot       = segment.conditions.weights.vehicle_mass_rate[:,0] / Units['kg/hr']
        fuel_burn  = TOW - mass
        body_angle = segment.conditions.frames.body.inertial_rotations[:,1,None] / Units.degrees
        throttle = segment.conditions.propulsion.throttle[:,0]
        
        axes = plt.subplot(2,1,1)
        axes.plot( time , mdot , line_color)
        axes.set_ylabel('Fuel Flow Rate (kg/hr)',axis_font)
        axes.set_xlabel('Time (mins)',axis_font)
        set_axes(axes)
        
        axes = plt.subplot(2,1,2)
        axes.plot( time , fuel_burn , line_color)
        axes.set_ylabel('Fuel burn (kg)',axis_font)
        axes.set_xlabel('Time (mins)',axis_font)
        set_axes(axes)
                
        with open(mdot_filename, 'a') as file:
            np.savetxt(file, mdot, delimiter=' ')
        
        with open(time_filename, 'a') as file:
            np.savetxt(file, time, delimiter=' ')
            
        with open(fuel_filename, 'a') as file:
            np.savetxt(file, fuel_burn, delimiter=' ')
        
        with open(pitch_filename, 'a') as file:
            np.savetxt(file, body_angle, delimiter=' ')
    
        with open(throttle_filename, 'a') as file:
            np.savetxt(file, throttle, delimiter=' ')
    
    #plt.savefig('/Users/lukeohagan/Library/CloudStorage/OneDrive-TrinityCollegeDublin/5th-Year/Research-Project/mySUAVE/Results/{}/{}/{}_FuelFlow.png').format(AC_reg, Flight_No, Flight_No)
    # plt.close()
     
    return

if __name__ == '__main__': 
    main()    
    plt.show()