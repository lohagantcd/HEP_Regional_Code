
import numpy as np
import matplotlib.pyplot as plt
import SUAVE

assert SUAVE.__version__=='2.5.2', 'These tutorials only work with the SUAVE 2.5.2 release'
from SUAVE.Core import Data, Units 
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
import vsp as vsp
print(vsp.GetVSPVersion())
from copy import deepcopy

def print_vsp_geometry_summary(vehicle):
    """Print a readable summary of all geometry imported via vsp_read()."""

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
 

def vehicle_setup():

    # vehicle = vsp_read(r"C:\Users\Luke TCD Woek\SUAVE\Tutorials-2.5.2\ATR_72-600\ATR72-600.vsp3", units_type='SI', specified_network=False)
    vehicle = vsp_read(r"C:\Users\OHAGANLU\SUAVE\Tutorials-2.5.2\ATR_72-600\ATR72-600_tcd_pc.vsp3", units_type='SI', specified_network=False)
    vehicle.tag = 'ATR_72-600'  

    vehicle.mass_properties.max_takeoff               = 22800 * Units.kilogram 
    vehicle.mass_properties.takeoff                   = 22800 * Units.kilogram   
    vehicle.mass_properties.operating_empty           = 13010 * Units.kilogram 
    vehicle.mass_properties.max_zero_fuel             = 20800 * Units.kilogram
    vehicle.mass_properties.cargo                     = 7550.  * Units.kilogram
    vehicle.envelope.ultimate_load = 3.75
    vehicle.envelope.limit_load    = 2.5
    vehicle.systems.control        = "fully powered" 
    vehicle.systems.accessories    = "medium range"
    vehicle.reference_area = vehicle.wings['wing'].areas.reference
    print("Area: ", vehicle.reference_area)
    
    wing_vsp = vehicle.wings.wing
    # This line adds a tag to the inside of the wing object but does not change the dictionary key of the componennt which stays as 'wing'
    wing_vsp.tag = 'main_wing' 
    wing_vsp.vertical = False
    wing_vsp.symmetric = True
    wing_vsp.high_lift = True
    # wing_vsp.dynamic_pressure_ratio = 1.0

    htail_vsp = vehicle.wings.htail
    htail_vsp.tag = 'horizontal_stabilizer'
    htail_vsp.vertical = False
    htail_vsp.symmetric = True
    htail_vsp.dynamic_pressure_ratio = 0.9
    
    vtail_vsp = vehicle.wings.vtail
    vtail_vsp.tag = 'vertical_stabilizer'
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
    nacelle1.diameter = 1.6* Units.meter
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
    turbofan.origin            = [[8.42146, 4.104, 1.014],[8.42146, -4.104, 1.014]] * Units.meter

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
 
    thrust.total_design             = 2*50000. * Units.N
    
    turbofan.thrust = thrust
    
    altitude      = 25000.0*Units.ft
    mach_number   = 0.6    

    turbofan_sizing(turbofan,mach_number,altitude)   

    vehicle.append_component(turbofan)    
    
    plot_vehicle(vehicle)

    return vehicle

if __name__ == '__main__': 
    vehicle = vehicle_setup()
    print_vsp_geometry_summary(vehicle)

    plt.show()

