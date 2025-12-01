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
from SUAVE.Core import Data, Units 
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
from SUAVE.Components.Wings.Segment import Segment
from SUAVE.Methods.Propulsion.propeller_design import *
from SUAVE.Components.Wings.Segment import Segment
# These are a variety of plotting routines that simplify the plotting process for commonly 
# requested metrics. Plots of specifically desired metrics can also be manually created.
from SUAVE.Methods.Propulsion.turbofan_sizing import turbofan_sizing
# Rather than conventional sizing, this script builds the turbofan energy network. This process is
# covered in more detail in a separate tutorial. It does not size the turbofan geometry.

from copy import deepcopy

def vehicle_setup():
    # This function creates the vehicle object for the ATR 72-600. It is broken into a separate
    # function to keep the tutorial organized, but this is not required. Note that some of the
    # values used here are estimates or approximations based on available public data. This is
    # sufficient for demonstration purposes, but should not be used for analysis requiring hig
    
    # ------------------------------------------------------------------
    #   Initialize the Vehicle
    # ------------------------------------------------------------------    
    
    vehicle = SUAVE.Vehicle()
    vehicle.tag = 'ATR_72-600'    
    
    # ------------------------------------------------------------------
    #   Vehicle-level Properties
    # ------------------------------------------------------------------    

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
    
    # Envelope properties
    # These values are typical FAR values for a transport of this type
    vehicle.envelope.ultimate_load = 3.75
    vehicle.envelope.limit_load    = 2.5

    # Vehicle level parameters
    # The vehicle reference area typically matches the main wing reference area 
    vehicle.reference_area         = 61 * Units['meters**2']  
    # Number of passengers, control settings, and accessories settings are used by the weights
    # methods
    vehicle.passengers             = 72
    vehicle.systems.control        = "fully powered" 
    vehicle.systems.accessories    = "medium range"

    # ------------------------------------------------------------------        
    #  Landing Gear
    # ------------------------------------------------------------------ 
    
    # The settings here can be used for noise analysis, but are not used in this tutorial
    landing_gear = SUAVE.Components.Landing_Gear.Landing_Gear()
    landing_gear.tag = "main_landing_gear"
    
    landing_gear.main_tire_diameter = 0.8636 * Units.m
    landing_gear.nose_tire_diameter = 0.44958 * Units.m
    landing_gear.main_strut_length  = 1.2 * Units.m
    landing_gear.nose_strut_length  = 1 * Units.m
    landing_gear.main_units  = 2    # Number of main landing gear
    landing_gear.nose_units  = 1    # Number of nose landing gear
    landing_gear.main_wheels = 2    # Number of wheels on the main landing gear
    landing_gear.nose_wheels = 2    # Number of wheels on the nose landing gear      
    vehicle.landing_gear = landing_gear

    # ------------------------------------------------------------------        
    #   Main Wing
    # ------------------------------------------------------------------        
    
    # This main wing is approximated as a simple trapezoid. A segmented wing can also be created if
    # desired. Segmented wings appear in later tutorials, and a version of the 737 with segmented
    # wings can be found in the SUAVE testing scripts.
    
    # SUAVE allows conflicting geometric values to be set in terms of items such as aspect ratio
    # when compared with span and reference area. Sizing scripts may be used to enforce 
    # consistency if desired.
    
        # === Main Wing ===
    wing = SUAVE.Components.Wings.Main_Wing()
    wing.tag = 'main_wing'

    wing.aspect_ratio            = 12
    wing.sweeps.quarter_chord    = 0 * Units.deg
    wing.thickness_to_chord      = 0.141
    wing.taper                   = 0.45
    wing.spans.projected         = 27.055499 * Units.meter
    wing.chords.root             = 2.626 * Units.meter
    wing.chords.tip              = 1.556 * Units.meter
    wing.chords.mean_aerodynamic = 2.2345 * Units.meter
    wing.areas.reference         = 61 * Units['meters**2']
    wing.twists.root             = 0 * Units.degrees
    wing.twists.tip              = 0 * Units.degrees
    wing.origin                  = [[27.166-10.594740,0,1.3345]] * Units.meter
    wing.vertical                = False
    wing.symmetric               = True
    wing.high_lift               = True
    wing.dynamic_pressure_ratio  = 2.0

        # Wing Segments
    segment                               = SUAVE.Components.Wings.Segment()
    segment.tag                           = 'Root'
    segment.percent_span_location         = 0.0
    segment.twist                         = 3. * Units.deg
    segment.root_chord_percent            = 1.
    segment.thickness_to_chord            = 0.141
    segment.dihedral_outboard             = 0 * Units.degrees
    segment.sweeps.quarter_chord          = 0
    wing.append_segment(segment)

    segment                               = SUAVE.Components.Wings.Segment()
    segment.tag                           = 'Break'
    segment.percent_span_location         = 0.2917
    segment.twist                         = 0. * Units.deg
    segment.root_chord_percent            = 1.0
    segment.thickness_to_chord            = 0.141
    segment.dihedral_outboard             = 0 * Units.degrees
    segment.sweeps.leading_edge           = 3.47 * Units.degrees
    segment.sweeps.trailing_edge             = -3.47 * Units.degrees
    wing.append_segment(segment)

    segment                               = SUAVE.Components.Wings.Segment()
    segment.tag                           = 'Tip'
    segment.percent_span_location         = 1.
    segment.twist                         = 1. * Units.degrees
    segment.root_chord_percent            = 0.5
    segment.thickness_to_chord            = 0.141
    segment.dihedral_outboard             = 0.
    segment.sweeps.quarter_chord          = 0.
    wing.append_segment(segment)

    wing = segment_properties(wing)        

    vehicle.append_component(wing)

    # ------------------------------------------------------------------
    #   Main Wing Control Surfaces
    # ------------------------------------------------------------------
    
    # Information in this section is used for high lift calculations and when conversion to AVL
    # is desired.
    
    # Deflections will typically be specified separately in individual vehicle configurations.
    
    flap                       = SUAVE.Components.Wings.Control_Surfaces.Flap() 
    flap.tag                   = 'flap' 
    flap.span_fraction_start   = 0.22 
    flap.span_fraction_end     = 0.7611
    flap.deflection            = 0.0 * Units.degrees
    # Flap configuration types are used in computing maximum CL and noise
    flap.configuration_type    = 'double_slotted'
    flap.chord_fraction        = 0.146
    wing.append_control_surface(flap)   
        
    # slat                       = SUAVE.Components.Wings.Control_Surfaces.Slat() 
    # slat.tag                   = 'slat' 
    # slat.span_fraction_start   = 0.324
    # slat.span_fraction_end     = 0.963     
    # slat.deflection            = 0.0 * Units.degrees
    # slat.chord_fraction        = 0.1  	 
    # wing.append_control_surface(slat)  
        
    aileron                       = SUAVE.Components.Wings.Control_Surfaces.Aileron() 
    aileron.tag                   = 'aileron' 
    aileron.span_fraction_start   = 0.761 
    aileron.span_fraction_end     = 1
    aileron.deflection            = 0.0 * Units.degrees
    aileron.chord_fraction        = 0.238 
    wing.append_control_surface(aileron)    
    
    # Add to vehicle
    vehicle.append_component(wing)    

    # ------------------------------------------------------------------        
    #  Horizontal Stabilizer
    # ------------------------------------------------------------------        
    
    wing = SUAVE.Components.Wings.Horizontal_Tail()
    wing.tag = 'horizontal_stabilizer'
    
    wing.aspect_ratio            = 5
    wing.sweeps.quarter_chord    = 5 * Units.deg
    wing.thickness_to_chord      = 0.2436
    wing.taper                   = 0.45
    wing.spans.projected         = 7.028513 * Units.meter
    wing.chords.root             = 2.02  * Units.meter
    wing.chords.tip              = 1.27 * Units.meter
    wing.chords.mean_aerodynamic = 1.389  * Units.meter
    wing.areas.reference         = 9.88   * Units['meters**2']  
    wing.twists.root             = 0 * Units.degrees
    wing.twists.tip              = 0 * Units.degrees  
    wing.origin                  = [[27.166 - 24.449400 * Units.meter, 0 , 4.488383 * Units.meter]]
    wing.vertical                = False 
    wing.symmetric               = True
    wing.dynamic_pressure_ratio  = 0.9  
    
    # Add to vehicle
    vehicle.append_component(wing)
    
    # ------------------------------------------------------------------
    #   Vertical Stabilizer
    # ------------------------------------------------------------------
    
   # === Vertical Tail (ATR 72-600) ===
    wing = SUAVE.Components.Wings.Vertical_Tail()
    wing.tag = 'vertical_tail'

    # Main geometry
    wing.areas.reference        = 9.446 * Units['meters**2']
    wing.aspect_ratio           = 1.3
    wing.taper                  = 0.65
    wing.sweeps.quarter_chord   = 25.0 * Units.degrees
    # wing.sweeps.leading_edge    = 28.718 * Units.degrees
    # wing.sweeps.trailing_edge   = 12.492 * Units.degrees
    wing.spans.projected        = 3.504 * Units.meter
    wing.chords.root            = 3.267 * Units.meter
    wing.chords.tip             = 2.124 * Units.meter
    wing.chords.mean_aerodynamic = 2.6 * Units.meter
    wing.symmetric              = False
    wing.vertical               = True
    wing.dynamic_pressure_ratio = 1.0

    # Tail position
    fuselage_length = 27.166 * Units.meter
    wing.origin = [[27.166-19.559520* Units.meter, 0.0* Units.meter, 0.0* Units.meter]]  # 72% of fuselage length

    # === Dorsal Fin Extension Data ===
    dorsal_span = 0.945 * Units.meter
    dorsal_root_chord = 2.9 * Units.meter
    dorsal_sweep_LE = 74.539 * Units.degrees

    # === Segments ===

    # Dorsal fin (base extension blending into fuselage)
    segment = Segment()
    segment.tag = 'dorsal_fin'
    segment.percent_span_location = 0.0
    segment.twist = 0.0 * Units.deg
    segment.root_chord_percent = dorsal_root_chord / wing.chords.root  # 2.9 / 3.267
    segment.thickness_to_chord = 0.10
    # segment.sweeps.leading_edge = dorsal_sweep_LE
    segment.sweeps.quarter_chord = 15.0 * Units.degrees
    # segment.dihedral_outboard = 90.0 * Units.degrees
    wing.append_segment(segment)

    # Lower fin (from dorsal to mid-span)
    segment = Segment()
    segment.tag = 'lower_fin'
    segment.percent_span_location = dorsal_span / wing.spans.projected  # 0.945 / 3.504 ≈ 0.27
    segment.twist = 0.0 * Units.deg
    segment.root_chord_percent = 1.0
    segment.thickness_to_chord = 0.10
    segment.sweeps.quarter_chord = 20.0 * Units.degrees
    segment.dihedral_outboard = 90.0 * Units.degrees
    wing.append_segment(segment)

    # Mid fin (main section)
    segment = Segment()
    segment.tag = 'mid_fin'
    segment.percent_span_location = 0.6
    segment.twist = 0.0 * Units.deg
    segment.root_chord_percent = 0.8
    segment.thickness_to_chord = 0.10
    segment.sweeps.quarter_chord = 25.0 * Units.degrees
    segment.dihedral_outboard = 90.0 * Units.degrees
    wing.append_segment(segment)

    # Tip fin
    segment = Segment()
    segment.tag = 'tip_fin'
    segment.percent_span_location = 1.0
    segment.twist = 0.0 * Units.deg
    segment.root_chord_percent = 0.65
    segment.thickness_to_chord = 0.10
    segment.sweeps.quarter_chord = 25.0 * Units.degrees
    segment.dihedral_outboard = 90.0 * Units.degrees
    wing.append_segment(segment)

    # Add to vehicle
    vehicle.append_component(wing)

    # ------------------------------------------------------------------
    #  Fuselage
    # ------------------------------------------------------------------
    
    fuselage = SUAVE.Components.Fuselages.Fuselage()
    fuselage.tag = 'fuselage'
    
    # Number of coach seats is used in some weights methods
    fuselage.number_coach_seats    = vehicle.passengers
    # The seats abreast can be used along with seat pitch and the number of coach seats to
    # determine the length of the cabin if desired.
    fuselage.seats_abreast         = 4
    fuselage.seat_pitch            = 0.7366     * Units.meter
    # Fineness ratios are used to determine VLM fuselage shape and sections to use in OpenVSP
    # output
    fuselage.fineness.nose         = 1.6
    fuselage.fineness.tail         = 2.
    # Nose and tail lengths are used in the VLM setup
    fuselage.lengths.nose          = 3.03   * Units.meter
    fuselage.lengths.tail          = 6.83   * Units.meter
    fuselage.lengths.total         = 27.166 * Units.meter
    # Fore and aft space are added to the cabin length if the fuselage is sized based on
    # number of seats
    fuselage.lengths.fore_space    = 1.    * Units.meter
    fuselage.lengths.aft_space     = 1.5    * Units.meter
    fuselage.width                 = 2.85  * Units.meter
    fuselage.heights.maximum       = 2.85  * Units.meter
    fuselage.effective_diameter    = 2.85     * Units.meter
    fuselage.areas.side_projected  = 77.42 * Units['meters**2'] 
    fuselage.areas.wetted          = 364  * Units['meters**2'] 
    fuselage.areas.front_projected = 6.38    * Units['meters**2'] 
    # Maximum differential pressure between the cabin and the atmosphere
    fuselage.differential_pressure = 5.0e4 * Units.pascal
    fuselage.origin                  = [[ 0* Units.meter, 0, 0 * Units.meter]] # meters
    
    # Heights at different longitudinal locations are used in stability calculations and
    # in output to OpenVSP
    fuselage.heights.at_quarter_length          = 2.85 * Units.meter
    fuselage.heights.at_three_quarters_length   = 2.02 * Units.meter
    fuselage.heights.at_wing_root_quarter_chord = 2.85 * Units.meter

    segment_nose1 = SUAVE.Components.Lofted_Body_Segment.Segment()
    segment_nose1.tag = 'nose1'
    segment_nose1.percent_x_location = 0.0
    segment_nose1.height = 1.6 * Units.meter
    segment_nose1.width  = 1.6 * Units.meter
    fuselage.Segments.append(segment_nose1)

    segment_nose2 = SUAVE.Components.Lofted_Body_Segment.Segment()
    segment_nose2.tag = 'nose2'
    segment_nose2.percent_x_location = 0.1
    segment_nose2.height = 2.2 * Units.meter
    segment_nose2.width  = 2.2 * Units.meter
    fuselage.Segments.append(segment_nose2)

    segment_nose3 = SUAVE.Components.Lofted_Body_Segment.Segment()
    segment_nose3.tag = 'nose3'
    segment_nose3.percent_x_location = 0.15
    segment_nose3.height = 2.85 * Units.meter
    segment_nose3.width  = 2.85 * Units.meter
    fuselage.Segments.append(segment_nose3)

    segment_nose4 = SUAVE.Components.Lofted_Body_Segment.Segment()
    segment_nose4.tag = 'nose4'
    segment_nose4.percent_x_location = 1
    segment_nose4.height = 2.85 * Units.meter
    segment_nose4.width  = 2.85 * Units.meter
    fuselage.Segments.append(segment_nose4)

    vehicle.append_component(fuselage)
    # ------------------------------------------------------------------
    #   Nacelles
    # ------------------------------------------------------------------ 
    # nacelle                       = SUAVE.Components.Nacelles.Nacelle()
    # nacelle.tag                   = 'nacelle_1'
    # nacelle.length                = 2.71
    # nacelle.inlet_diameter        = 1.90
    # nacelle.diameter              = 2.05
    # nacelle.areas.wetted          = 1.1*np.pi*nacelle.diameter*nacelle.length
    # nacelle.origin                = [[13.72, -4.86,-1.9]]
    # nacelle.flow_through          = True  
    # nacelle_airfoil               = SUAVE.Components.Airfoils.Airfoil() 
    # nacelle_airfoil.naca_4_series_airfoil = '2410'
    # nacelle.append_airfoil(nacelle_airfoil)

    # nacelle_2                     = deepcopy(nacelle)
    # nacelle_2.tag                 = 'nacelle_2'
    # nacelle_2.origin              = [[13.72, 4.86,-1.9]]
    
    # vehicle.append_component(nacelle)  
    # vehicle.append_component(nacelle_2)     
        
    # prop = propeller_design(
    #     # vehicle.mass_properties.max_takeoff,
    #     #                     vehicle.reference_area,
    #                         # num_propellers=6,
    #                         # cruise_speed=510*Units.km/Units.hr,
    #                         # cruise_altitude=7620*Units.m,
    #                         # shaft_hp=2000,
    #                         # prop_efficiency=0.85
    #                         )
    # prop.tag = 'left_prop'
    # prop.origin = [[13.72, -4.86, -1.9]] * Units.m
    # prop.diameter = 3.93 * Units.m
    # prop.number_of_blades = 6
    # vehicle.append_component(prop)

    # prop_right = deepcopy(prop)
    # prop_right.tag = 'right_prop'
    # prop_right.origin = [[13.72, 4.86, -1.9]] * Units.m
    # vehicle.append_component(prop_right)

    
    # ------------------------------------------------------------------
    #   Vehicle Definition Complete
    # ------------------------------------------------------------------
    plot_vehicle(vehicle)
    return vehicle

if __name__ == '__main__': 
    vehicle = vehicle_setup()
    # The show commands makes the plots actually appear
    plt.show()

