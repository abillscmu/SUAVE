## @ingroup Methods-Aerodynamics-Common-Fidelity_Zero-Lift
# compute_vortex_distribution.py
# 
# Created:  May 2018, M. Clarke

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# package imports
import SUAVE
import numpy as np
from SUAVE.Core import Units , Data
from SUAVE.Methods.Aerodynamics.XFOIL.compute_airfoil_polars import read_wing_airfoil

## @ingroup Methods-Aerodynamics-Common-Fidelity_Zero-Lift
def compute_vortex_distribution(geometry,settings):
    # ---------------------------------------------------------------------------------------
    # STEP 1: Define empty vectors for coordinates of panes, control points and bound vortices
    # ---------------------------------------------------------------------------------------
    VD = Data()
 
    VD.XAH = np.empty(shape=[0,1])
    VD.YAH = np.empty(shape=[0,1])
    VD.ZAH = np.empty(shape=[0,1])
    VD.XBH = np.empty(shape=[0,1])
    VD.YBH = np.empty(shape=[0,1])
    VD.ZBH = np.empty(shape=[0,1])
    VD.XCH = np.empty(shape=[0,1])
    VD.YCH = np.empty(shape=[0,1])
    VD.ZCH = np.empty(shape=[0,1])     
    VD.XA1 = np.empty(shape=[0,1])
    VD.YA1 = np.empty(shape=[0,1])  
    VD.ZA1 = np.empty(shape=[0,1])
    VD.XA2 = np.empty(shape=[0,1])
    VD.YA2 = np.empty(shape=[0,1])    
    VD.ZA2 = np.empty(shape=[0,1])    
    VD.XB1 = np.empty(shape=[0,1])
    VD.YB1 = np.empty(shape=[0,1])  
    VD.ZB1 = np.empty(shape=[0,1])
    VD.XB2 = np.empty(shape=[0,1])
    VD.YB2 = np.empty(shape=[0,1])    
    VD.ZB2 = np.empty(shape=[0,1])     
    VD.XAC = np.empty(shape=[0,1])
    VD.YAC = np.empty(shape=[0,1])
    VD.ZAC = np.empty(shape=[0,1]) 
    VD.XBC = np.empty(shape=[0,1])
    VD.YBC = np.empty(shape=[0,1])
    VD.ZBC = np.empty(shape=[0,1])     
    VD.XC = np.empty(shape=[0,1])
    VD.YC = np.empty(shape=[0,1])
    VD.ZC = np.empty(shape=[0,1])     
    VD.CS = np.empty(shape=[0,1]) 
    
    n_sw = settings.number_panels_spanwise 
    n_cw = settings.number_panels_chordwise     

    # ---------------------------------------------------------------------------------------
    # STEP 2: Unpack aircraft wing geometry 
    # ---------------------------------------------------------------------------------------    
    n_w = 0 # number of wings 
    n_cp = 0 # number of bound vortices        
    wing_areas = [] # wing areas         
    for wing in geometry.wings:
        span        = wing.spans.projected
        root_chord  = wing.chords.root
        tip_chord   = wing.chords.tip
        sweep_qc    = wing.sweeps.quarter_chord
        sweep_le    = wing.sweeps.leading_edge
        taper       = wing.taper
        twist_rc    = wing.twists.root
        twist_tc    = wing.twists.tip
        dihedral    = wing.dihedral
        sym_para    = wing.symmetric
        Sref        = wing.areas.reference
        vertical_wing = wing.vertical
        wing_origin = wing.origin
    
        # determine of vehicle has symmetry 
        if sym_para is True :
            span = span/2
            
        si  = np.arange(1,((n_sw*2)+2))
        spacing = np.cos((2*si - 1)/(2*len(si))*np.pi)
        y_coordinates  = span*spacing[0:int((len(si)+1)/2)][::-1]                 
        y_a   = y_coordinates[:-1] 
        y_b   = y_coordinates[1:] 
        
        xah = np.zeros(n_cw*n_sw)
        yah = np.zeros(n_cw*n_sw)
        zah = np.zeros(n_cw*n_sw)
        xbh = np.zeros(n_cw*n_sw)
        ybh = np.zeros(n_cw*n_sw)
        zbh = np.zeros(n_cw*n_sw)    
        xch = np.zeros(n_cw*n_sw)
        ych = np.zeros(n_cw*n_sw)
        zch = np.zeros(n_cw*n_sw)    
        xa1 = np.zeros(n_cw*n_sw)
        ya1 = np.zeros(n_cw*n_sw)
        za1 = np.zeros(n_cw*n_sw)
        xa2 = np.zeros(n_cw*n_sw)
        ya2 = np.zeros(n_cw*n_sw)
        za2 = np.zeros(n_cw*n_sw)    
        xb1 = np.zeros(n_cw*n_sw)
        yb1 = np.zeros(n_cw*n_sw)
        zb1 = np.zeros(n_cw*n_sw)
        xb2 = np.zeros(n_cw*n_sw) 
        yb2 = np.zeros(n_cw*n_sw) 
        zb2 = np.zeros(n_cw*n_sw)    
        xac = np.zeros(n_cw*n_sw)
        yac = np.zeros(n_cw*n_sw)
        zac = np.zeros(n_cw*n_sw)    
        xbc = np.zeros(n_cw*n_sw)
        ybc = np.zeros(n_cw*n_sw)
        zbc = np.zeros(n_cw*n_sw)    
        xc  = np.zeros(n_cw*n_sw) 
        yc  = np.zeros(n_cw*n_sw) 
        zc  = np.zeros(n_cw*n_sw)
         
        cs_w = np.zeros(n_sw)
               
        # ---------------------------------------------------------------------------------------
        # STEP 3: Determine if wing segments are defined  
        # ---------------------------------------------------------------------------------------
        n_segments           = len(wing.Segments.keys())
        if n_segments>0:            
            # ---------------------------------------------------------------------------------------
            # STEP 4A: Discretizing the wing sections into panels
            # ---------------------------------------------------------------------------------------
            segment_chord          = np.zeros(n_segments)
            segment_twist          = np.zeros(n_segments)
            segment_sweep          = np.zeros(n_segments)
            segment_span           = np.zeros(n_segments)
            segment_area           = np.zeros(n_segments)
            segment_dihedral       = np.zeros(n_segments)
            segment_x_coord        = [] 
            segment_camber         = []
            segment_chord_x_offset = np.zeros(n_segments)
            segment_chord_z_offset = np.zeros(n_segments)
            section_stations       = np.zeros(n_segments) 
            
            # ---------------------------------------------------------------------------------------
            # STEP 5A: Obtain sweep, chord, dihedral and twist at the beginning/end of each segment.
            #          If applicable, append airfoil section VD and flap/aileron deflection angles.
            # ---------------------------------------------------------------------------------------
            segment_sweeps = []
            for i_seg in range(n_segments):   
                segment_chord[i_seg]    = wing.Segments[i_seg].root_chord_percent*root_chord
                segment_twist[i_seg]    = wing.Segments[i_seg].twist
                section_stations[i_seg] = wing.Segments[i_seg].percent_span_location*span  
                segment_dihedral[i_seg] = wing.Segments[i_seg].dihedral_outboard                    
        
                # change to leading edge sweep, if quarter chord sweep givent, convert to leading edge sweep 
                if (i_seg == n_segments-1):
                    segment_sweep[i_seg] = 0                                  
                else: 
                    if wing.Segments[i_seg].sweeps.leading_edge != None:
                        segment_sweep[i_seg] = wing.Segments[i_seg].sweeps.leading_edge
                    else:                                                                 
                        sweep_quarter_chord  = wing.Segments[i_seg].sweeps.quarter_chord
                        cf       = 0.25                          
                        seg_root_chord       = root_chord*wing.Segments[i_seg].root_chord_percent
                        seg_tip_chord        = root_chord*wing.Segments[i_seg+1].root_chord_percent
                        seg_span             = span*(wing.Segments[i_seg+1].percent_span_location - wing.Segments[i_seg].percent_span_location )
                        segment_sweep[i_seg] = np.arctan(((seg_root_chord*cf) + (np.tan(sweep_quarter_chord)*seg_span - cf*seg_tip_chord)) /seg_span)  
        
                if i_seg == 0:
                    segment_span[i_seg]           = 0.0
                    segment_chord_x_offset[i_seg] = 0.0  
                    segment_chord_z_offset[i_seg] = 0.0
                else:
                    segment_span[i_seg]           = wing.Segments[i_seg].percent_span_location*span - wing.Segments[i_seg-1].percent_span_location*span
                    segment_chord_x_offset[i_seg] = segment_chord_x_offset[i_seg-1] + segment_span[i_seg]*np.tan(segment_sweep[i_seg-1])
                    segment_chord_z_offset[i_seg] = segment_chord_z_offset[i_seg-1] + segment_span[i_seg]*np.tan(segment_dihedral[i_seg-1])
                
                # Get airfoil section VD  
                if wing.Segments[i_seg].Airfoil: 
                    airfoil_data = read_wing_airfoil(wing.Segments[i_seg].Airfoil.airfoil.coordinate_file )    
                    segment_camber.append(airfoil_data.camber_coordinates)
                    segment_x_coord.append(airfoil_data.x_lower_surface) 
                else:
                    segment_camber.append(np.zeros(30))              
                    segment_x_coord.append(np.linspace(0,1,30)) 
               
                # ** TO DO ** Get flap/aileron locations and deflection
                
            wing_areas.append(np.sum(segment_area[:]))
            if sym_para is True :
                wing_areas.append(np.sum(segment_area[:]))
                
            #Shift spanwise vortices onto section breaks  
            for i_seg in range(n_segments):
                idx =  (np.abs(y_coordinates-section_stations[i_seg])).argmin()
                y_coordinates[idx] = section_stations[i_seg]                
 

            #y_coordinates[(np.abs(y_coordinates-section_stations[:])).argmin()] = section_stations[:]
                
            # ---------------------------------------------------------------------------------------
            # STEP 6A: Define coordinates of panels horseshoe vortices and control points 
            # ---------------------------------------------------------------------------------------
            del_y = y_coordinates[1:] - y_coordinates[:-1]
        
            # trial 
            #seg_idx = np.zeros(n_cw*n_sw) 
            #i_seg = 0
            #for idx_y in range(n_sw):
                #if y_coordinates[idx_y] == wing.Segments[i_seg+1].percent_span_location*span: 
                    #i_seg += 1                
                #seg_idx[idx_y] = i_seg   
                ##if y_coordinates[idx_y+1] == span:
                    ##continue  
                
            # define coordinates of horseshoe vortices and control points
            i_seg = 0           
            for idx_y in range(n_sw):
                idx_x = np.arange(n_cw) 
                eta_a = (y_a[idx_y] - section_stations[i_seg])  
                eta_b = (y_b[idx_y] - section_stations[i_seg]) 
                eta   = (y_b[idx_y] - del_y[idx_y]/2 - section_stations[i_seg]) 
                
                segment_chord_ratio = (segment_chord[i_seg+1] - segment_chord[i_seg])/segment_span[i_seg+1]
                segment_twist_ratio = (segment_twist[i_seg+1] - segment_twist[i_seg])/segment_span[i_seg+1]
                
                wing_chord_section_a  = segment_chord[i_seg] + (eta_a*segment_chord_ratio) 
                wing_chord_section_b  = segment_chord[i_seg] + (eta_b*segment_chord_ratio)
                wing_chord_section    = segment_chord[i_seg] + (eta*segment_chord_ratio)
                
                delta_x_a = wing_chord_section_a/n_cw  
                delta_x_b = wing_chord_section_b/n_cw      
                delta_x   = wing_chord_section/n_cw                                       
                
                xi_a1 = segment_chord_x_offset[i_seg] + eta_a*np.tan(segment_sweep[i_seg]) + delta_x_a*idx_x                  # x coordinate of top left corner of panel
                xi_ah = segment_chord_x_offset[i_seg] + eta_a*np.tan(segment_sweep[i_seg]) + delta_x_a*idx_x + delta_x_a*0.25 # x coordinate of left corner of panel
                xi_a2 = segment_chord_x_offset[i_seg] + eta_a*np.tan(segment_sweep[i_seg]) + delta_x_a*idx_x + delta_x_a      # x coordinate of bottom left corner of bound vortex 
                xi_ac = segment_chord_x_offset[i_seg] + eta_a*np.tan(segment_sweep[i_seg]) + delta_x_a*idx_x + delta_x_a*0.75 # x coordinate of bottom left corner of control point vortex  
                xi_b1 = segment_chord_x_offset[i_seg] + eta_b*np.tan(segment_sweep[i_seg]) + delta_x_b*idx_x                  # x coordinate of top right corner of panel      
                xi_bh = segment_chord_x_offset[i_seg] + eta_b*np.tan(segment_sweep[i_seg]) + delta_x_b*idx_x + delta_x_b*0.25 # x coordinate of right corner of bound vortex         
                xi_b2 = segment_chord_x_offset[i_seg] + eta_b*np.tan(segment_sweep[i_seg]) + delta_x_b*idx_x + delta_x_b      # x coordinate of bottom right corner of panel
                xi_bc = segment_chord_x_offset[i_seg] + eta_b*np.tan(segment_sweep[i_seg]) + delta_x_b*idx_x + delta_x_b*0.75 # x coordinate of bottom right corner of control point vortex         
                xi_c  = segment_chord_x_offset[i_seg] + eta *np.tan(segment_sweep[i_seg])  + delta_x  *idx_x + delta_x*0.75   # x coordinate three-quarter chord control point for each panel
                xi_ch = segment_chord_x_offset[i_seg] + eta *np.tan(segment_sweep[i_seg])  + delta_x  *idx_x + delta_x*0.25   # x coordinate center of bound vortex of each panel 

                # camber
                section_camber_a  = segment_camber[i_seg]*wing_chord_section_a  
                section_camber_b  = segment_camber[i_seg]*wing_chord_section_b  
                section_camber_c    = segment_camber[i_seg]*wing_chord_section                
                section_x_coord_a = segment_x_coord[i_seg]*wing_chord_section_a
                section_x_coord_b = segment_x_coord[i_seg]*wing_chord_section_b
                section_x_coord   = segment_x_coord[i_seg]*wing_chord_section
                
                z_c_a1 = np.interp((idx_x    *delta_x_a)                  ,section_x_coord_a,section_camber_a) 
                z_c_ah = np.interp((idx_x    *delta_x_a + delta_x_a*0.25) ,section_x_coord_a,section_camber_a)
                z_c_a2 = np.interp(((idx_x+1)*delta_x_a)                  ,section_x_coord_a,section_camber_a) 
                z_c_ac = np.interp((idx_x    *delta_x_a + delta_x_a*0.75) ,section_x_coord_a,section_camber_a) 
                z_c_b1 = np.interp((idx_x    *delta_x_b)                  ,section_x_coord_b,section_camber_b)   
                z_c_bh = np.interp((idx_x    *delta_x_b + delta_x_b*0.25) ,section_x_coord_b,section_camber_b) 
                z_c_b2 = np.interp(((idx_x+1)*delta_x_b)                  ,section_x_coord_b,section_camber_b) 
                z_c_bc = np.interp((idx_x    *delta_x_b + delta_x_b*0.75) ,section_x_coord_b,section_camber_b) 
                z_c    = np.interp((idx_x    *delta_x   + delta_x  *0.75) ,section_x_coord,section_camber_c) 
                z_c_ch = np.interp((idx_x    *delta_x   + delta_x  *0.25) ,section_x_coord,section_camber_c) 
                
                zeta_a1 = segment_chord_z_offset[i_seg] + eta_a*np.tan(segment_dihedral[i_seg])  + z_c_a1  # z coordinate of top left corner of panel
                zeta_ah = segment_chord_z_offset[i_seg] + eta_a*np.tan(segment_dihedral[i_seg])  + z_c_ah  # z coordinate of left corner of bound vortex  
                zeta_a2 = segment_chord_z_offset[i_seg] + eta_a*np.tan(segment_dihedral[i_seg])  + z_c_a2  # z coordinate of bottom left corner of panel
                zeta_ac = segment_chord_z_offset[i_seg] + eta_a*np.tan(segment_dihedral[i_seg])  + z_c_ac  # z coordinate of bottom left corner of panel of control point
                zeta_bc = segment_chord_z_offset[i_seg] + eta_b*np.tan(segment_dihedral[i_seg])  + z_c_bc  # z coordinate of top right corner of panel of control point                          
                zeta_b1 = segment_chord_z_offset[i_seg] + eta_b*np.tan(segment_dihedral[i_seg])  + z_c_b1  # z coordinate of top right corner of panel  
                zeta_bh = segment_chord_z_offset[i_seg] + eta_b*np.tan(segment_dihedral[i_seg])  + z_c_bh  # z coordinate of right corner of bound vortex        
                zeta_b2 = segment_chord_z_offset[i_seg] + eta_b*np.tan(segment_dihedral[i_seg])  + z_c_b2  # z coordinate of bottom right corner of panel                 
                zeta    = segment_chord_z_offset[i_seg] + eta*np.tan(segment_dihedral[i_seg])    + z_c     # z coordinate three-quarter chord control point for each panel
                zeta_ch = segment_chord_z_offset[i_seg] + eta*np.tan(segment_dihedral[i_seg])    + z_c_ch  # z coordinate center of bound vortex on each panel
                
                # adjustment of panels for twist  
                xi_LE_a = segment_chord_x_offset[i_seg] + eta_a*np.tan(segment_sweep[i_seg])               # x location of leading edge left corner of wing
                xi_LE_b = segment_chord_x_offset[i_seg] + eta_b*np.tan(segment_sweep[i_seg])               # x location of leading edge right of wing
                xi_LE   = segment_chord_x_offset[i_seg] + eta*np.tan(segment_sweep[i_seg])                 # x location of leading edge center of wing
                
                zeta_LE_a = segment_chord_z_offset[i_seg] + eta_a*np.tan(segment_dihedral[i_seg])          # z location of leading edge left corner of wing
                zeta_LE_b = segment_chord_z_offset[i_seg] + eta_b*np.tan(segment_dihedral[i_seg])          # z location of leading edge right of wing
                zeta_LE   = segment_chord_z_offset[i_seg] + eta*np.tan(segment_dihedral[i_seg])            # z location of leading edge center of wing
                
                # determine section twist
                section_twist_a = segment_twist[i_seg] + (eta_a * segment_twist_ratio)                     # twist at left side of panel
                section_twist_b = segment_twist[i_seg] + (eta_b * segment_twist_ratio)                     # twist at right side of panel
                section_twist   = segment_twist[i_seg] + (eta* segment_twist_ratio)                        # twist at center local chord 
                
                xi_prime_a1  = xi_LE_a + np.cos(section_twist_a)*(xi_a1-xi_LE_a) + np.sin(section_twist_a)*(zeta_a1-zeta_LE_a)   # x coordinate transformation of top left corner
                xi_prime_ah  = xi_LE_a + np.cos(section_twist_a)*(xi_ah-xi_LE_a) + np.sin(section_twist_a)*(zeta_ah-zeta_LE_a)   # x coordinate transformation of bottom left corner
                xi_prime_a2  = xi_LE_a + np.cos(section_twist_a)*(xi_a2-xi_LE_a) + np.sin(section_twist_a)*(zeta_a2-zeta_LE_a)   # x coordinate transformation of bottom left corner
                xi_prime_ac  = xi_LE_a + np.cos(section_twist_a)*(xi_ac-xi_LE_a) + np.sin(section_twist_a)*(zeta_a2-zeta_LE_a)   # x coordinate transformation of bottom left corner of control point
                xi_prime_bc  = xi_LE_b + np.cos(section_twist_b)*(xi_bc-xi_LE_b) + np.sin(section_twist_b)*(zeta_b1-zeta_LE_b)   # x coordinate transformation of top right corner of control point                         
                xi_prime_b1  = xi_LE_b + np.cos(section_twist_b)*(xi_b1-xi_LE_b) + np.sin(section_twist_b)*(zeta_b1-zeta_LE_b)   # x coordinate transformation of top right corner 
                xi_prime_bh  = xi_LE_b + np.cos(section_twist_b)*(xi_bh-xi_LE_b) + np.sin(section_twist_b)*(zeta_bh-zeta_LE_b)   # x coordinate transformation of top right corner 
                xi_prime_b2  = xi_LE_b + np.cos(section_twist_b)*(xi_b2-xi_LE_b) + np.sin(section_twist_b)*(zeta_b2-zeta_LE_b)   # x coordinate transformation of botton right corner 
                xi_prime     = xi_LE   + np.cos(section_twist)  *(xi_c-xi_LE)    + np.sin(section_twist)*(zeta-zeta_LE)          # x coordinate transformation of control point
                xi_prime_ch  = xi_LE   + np.cos(section_twist)  *(xi_ch-xi_LE)   + np.sin(section_twist)*(zeta_ch-zeta_LE)       # x coordinate transformation of center of horeshoe vortex 
                
                zeta_prime_a1  = zeta_LE_a - np.sin(section_twist_a)*(xi_a1-xi_LE_a) + np.cos(section_twist_a)*(zeta_a1-zeta_LE_a) # z coordinate transformation of top left corner
                zeta_prime_ah  = zeta_LE_a - np.sin(section_twist_a)*(xi_ah-xi_LE_a) + np.cos(section_twist_a)*(zeta_ah-zeta_LE_a) # z coordinate transformation of bottom left corner
                zeta_prime_a2  = zeta_LE_a - np.sin(section_twist_a)*(xi_a2-xi_LE_a) + np.cos(section_twist_a)*(zeta_a2-zeta_LE_a) # z coordinate transformation of bottom left corner
                zeta_prime_ac  = zeta_LE_a - np.sin(section_twist_a)*(xi_ac-xi_LE_a) + np.cos(section_twist_a)*(zeta_ac-zeta_LE_a) # z coordinate transformation of bottom left corner
                zeta_prime_bc  = zeta_LE_b - np.sin(section_twist_b)*(xi_bc-xi_LE_b) + np.cos(section_twist_b)*(zeta_bc-zeta_LE_b) # z coordinate transformation of top right corner                         
                zeta_prime_b1  = zeta_LE_b - np.sin(section_twist_b)*(xi_b1-xi_LE_b) + np.cos(section_twist_b)*(zeta_b1-zeta_LE_b) # z coordinate transformation of top right corner 
                zeta_prime_bh  = zeta_LE_b - np.sin(section_twist_b)*(xi_bh-xi_LE_b) + np.cos(section_twist_b)*(zeta_bh-zeta_LE_b) # z coordinate transformation of top right corner 
                zeta_prime_b2  = zeta_LE_b - np.sin(section_twist_b)*(xi_b2-xi_LE_b) + np.cos(section_twist_b)*(zeta_b2-zeta_LE_b) # z coordinate transformation of botton right corner 
                zeta_prime     = zeta_LE   - np.sin(section_twist)*(xi_c-xi_LE) + np.cos(-section_twist)*(zeta-zeta_LE)            # z coordinate transformation of control point
                zeta_prime_ch   = zeta_LE   - np.sin(section_twist)*(xi_ch-xi_LE) + np.cos(-section_twist)*(zeta_ch-zeta_LE)            # z coordinate transformation of center of horseshoe
                                       
                # ** TO DO ** Get flap/aileron locations and deflection
                
                # store coordinates of panels, horseshoeces vortices and control points relative to wing root 
                if vertical_wing:
                    xa1[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_a1 
                    za1[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_a[idx_y]
                    ya1[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_a1
                    xa2[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_a2
                    za2[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_a[idx_y]
                    ya2[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_a2
                        
                    xb1[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_b1 
                    zb1[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_b[idx_y]
                    yb1[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_b1
                    xb2[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_b2 
                    zb2[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_b[idx_y]                        
                    yb2[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_b2 
                         
                    xah[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_ah
                    zah[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_a[idx_y]
                    yah[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_ah                    
                    xbh[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_bh 
                    zbh[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_b[idx_y]
                    ybh[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_bh
                          
                    xch[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_ch
                    zch[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*(y_b[idx_y] - del_y[idx_y]/2)                   
                    ych[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_ch
                          
                    xc [idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime 
                    zc [idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*(y_b[idx_y] - del_y[idx_y]/2) 
                    yc [idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime 
                         
                    xac[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_ac 
                    zac[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_a[idx_y]
                    yac[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_ac
                    xbc[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_bc
                    zbc[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_b[idx_y]                            
                    ybc[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_bc                        
                          
                else:     
                    xa1[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_a1 
                    ya1[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_a[idx_y]
                    za1[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_a1
                    xa2[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_a2
                    ya2[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_a[idx_y]
                    za2[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_a2
                         
                    xb1[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_b1 
                    yb1[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_b[idx_y]
                    zb1[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_b1
                    yb2[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_b[idx_y]
                    xb2[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_b2 
                    zb2[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_b2 
                         
                    xah[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_ah
                    yah[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_a[idx_y]
                    zah[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_ah                    
                    xbh[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_bh 
                    ybh[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_b[idx_y]
                    zbh[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_bh
                         
                    xch[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_ch
                    ych[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*(y_b[idx_y] - del_y[idx_y]/2)                    
                    zch[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_ch
                         
                    xc [idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime 
                    yc [idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*(y_b[idx_y] - del_y[idx_y]/2)
                    zc [idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime 
                      
                    xac[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_ac 
                    yac[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_a[idx_y]
                    zac[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_ac
                    xbc[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_bc
                    ybc[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_b[idx_y]                            
                    zbc[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_bc   
                    
                idx += 1
                
                cs_w[idx_y] = wing_chord_section       
            
                if y_coordinates[idx_y] == wing.Segments[i_seg+1].percent_span_location*span: 
                    i_seg += 1                
                if y_coordinates[idx_y+1] == span:
                    continue                                      
                                                    
        else:   # when no segments are defined on wing  
            # ---------------------------------------------------------------------------------------
            # STEP 6B: Define coordinates of panels horseshoe vortices and control points 
            # ---------------------------------------------------------------------------------------
            
            if sweep_le != 0:
                sweep = sweep_le
            else:                                                                
                cf    = 0.25                          
                sweep = np.arctan(((root_chord*cf) + (np.tan(sweep_qc)*span - cf*tip_chord)) /span)  
     
            i    = np.arange(0,n_sw)             
            wing_chord_ratio = (tip_chord-root_chord)/span
            wing_twist_ratio = (twist_tc-twist_rc)/span                    
            wing_areas.append(0.5*(root_chord+tip_chord)*span) 
            if sym_para is True :
                wing_areas.append(0.5*(root_chord+tip_chord)*span)   
            
            # Get airfoil section VD  
            if wing.Airfoil: 
                airfoil_data = read_wing_airfoil(wing.Airfoil.airfoil.coordinate_file)    
                wing_camber  = airfoil_data.camber_coordinates
                wing_x_coord = airfoil_data.x_lower_surface
            else:
                wing_camber  = np.zeros(30) # dimension of Selig airfoil VD file
                wing_x_coord = np.linspace(0,1,30)

            delta_y = y_b - y_a
            for idx_y in range(n_sw):  
                idx_x = np.arange(n_cw) 
                eta_a = (y_a[idx_y])  
                eta_b = (y_b[idx_y]) 
                eta   = (y_b[idx_y] - delta_y[idx_y]/2) 
                 
                wing_chord_section_a  = root_chord + (eta_a*wing_chord_ratio) 
                wing_chord_section_b  = root_chord + (eta_b*wing_chord_ratio)
                wing_chord_section    = root_chord + (eta*wing_chord_ratio)
                
                delta_x_a = wing_chord_section_a/n_cw   
                delta_x_b = wing_chord_section_b/n_cw   
                delta_x   = wing_chord_section/n_cw                                  
                
                xi_a1 = eta_a*np.tan(sweep) + delta_x_a*idx_x                  # x coordinate of top left corner of panel
                xi_ah = eta_a*np.tan(sweep) + delta_x_a*idx_x + delta_x_a*0.25 # x coordinate of left corner of panel
                xi_a2 = eta_a*np.tan(sweep) + delta_x_a*idx_x + delta_x_a      # x coordinate of bottom left corner of bound vortex 
                xi_ac = eta_a*np.tan(sweep) + delta_x_a*idx_x + delta_x_a*0.75 # x coordinate of bottom left corner of control point vortex  
                xi_b1 = eta_b*np.tan(sweep) + delta_x_b*idx_x                  # x coordinate of top right corner of panel      
                xi_bh = eta_b*np.tan(sweep) + delta_x_b*idx_x + delta_x_b*0.25 # x coordinate of right corner of bound vortex         
                xi_b2 = eta_b*np.tan(sweep) + delta_x_b*idx_x + delta_x_b      # x coordinate of bottom right corner of panel
                xi_bc = eta_b*np.tan(sweep) + delta_x_b*idx_x + delta_x_b*0.75 # x coordinate of bottom right corner of control point vortex         
                xi_c  =  eta *np.tan(sweep)  + delta_x  *idx_x + delta_x*0.75   # x coordinate three-quarter chord control point for each panel
                xi_ch =  eta *np.tan(sweep)  + delta_x  *idx_x + delta_x*0.25   # x coordinate center of bound vortex of each panel 
                                  
                section_camber_a  = wing_camber*wing_chord_section_a
                section_camber_b  = wing_camber*wing_chord_section_b  
                section_camber_c  = wing_camber*wing_chord_section
                                       
                section_x_coord_a = wing_x_coord*wing_chord_section_a
                section_x_coord_b = wing_x_coord*wing_chord_section_b
                section_x_coord   = wing_x_coord*wing_chord_section
                
                z_c_a1 = np.interp((idx_x    *delta_x_a)                  ,section_x_coord_a,section_camber_a) 
                z_c_ah = np.interp((idx_x    *delta_x_a + delta_x_a*0.25) ,section_x_coord_a,section_camber_a)
                z_c_a2 = np.interp(((idx_x+1)*delta_x_a)                  ,section_x_coord_a,section_camber_a) 
                z_c_ac = np.interp((idx_x    *delta_x_a + delta_x_a*0.75) ,section_x_coord_a,section_camber_a) 
                z_c_b1 = np.interp((idx_x    *delta_x_b)                  ,section_x_coord_b,section_camber_b)   
                z_c_bh = np.interp((idx_x    *delta_x_b + delta_x_b*0.25) ,section_x_coord_b,section_camber_b) 
                z_c_b2 = np.interp(((idx_x+1)*delta_x_b)                  ,section_x_coord_b,section_camber_b) 
                z_c_bc = np.interp((idx_x    *delta_x_b + delta_x_b*0.75) ,section_x_coord_b,section_camber_b) 
                z_c    = np.interp((idx_x    *delta_x   + delta_x  *0.75) ,section_x_coord  ,section_camber_c) 
                z_c_ch = np.interp((idx_x    *delta_x   + delta_x  *0.25) ,section_x_coord  ,section_camber_c) 
                
                zeta_a1 = eta_a*np.tan(dihedral)  + z_c_a1  # z coordinate of top left corner of panel
                zeta_ah = eta_a*np.tan(dihedral)  + z_c_ah  # z coordinate of left corner of bound vortex  
                zeta_a2 = eta_a*np.tan(dihedral)  + z_c_a2  # z coordinate of bottom left corner of panel
                zeta_ac = eta_a*np.tan(dihedral)  + z_c_ac  # z coordinate of bottom left corner of panel of control point
                zeta_bc = eta_b*np.tan(dihedral)  + z_c_bc  # z coordinate of top right corner of panel of control point                          
                zeta_b1 = eta_b*np.tan(dihedral)  + z_c_b1  # z coordinate of top right corner of panel  
                zeta_bh = eta_b*np.tan(dihedral)  + z_c_bh  # z coordinate of right corner of bound vortex        
                zeta_b2 = eta_b*np.tan(dihedral)  + z_c_b2  # z coordinate of bottom right corner of panel                 
                zeta    =   eta*np.tan(dihedral)    + z_c     # z coordinate three-quarter chord control point for each panel
                zeta_ch =   eta*np.tan(dihedral)    + z_c_ch  # z coordinate center of bound vortex on each panel
                                                     
                # adjustment of panels for twist  
                xi_LE_a = eta_a*np.tan(sweep)               # x location of leading edge left corner of wing
                xi_LE_b = eta_b*np.tan(sweep)               # x location of leading edge right of wing
                xi_LE   = eta  *np.tan(sweep)               # x location of leading edge center of wing
                
                zeta_LE_a = eta_a*np.tan(dihedral)          # z location of leading edge left corner of wing
                zeta_LE_b = eta_b*np.tan(dihedral)          # z location of leading edge right of wing
                zeta_LE   = eta  *np.tan(dihedral)          # z location of leading edge center of wing
                
                # determine section twist
                section_twist_a = twist_rc + (eta_a * wing_twist_ratio)                     # twist at left side of panel
                section_twist_b = twist_rc + (eta_b * wing_twist_ratio)                     # twist at right side of panel
                section_twist   = twist_rc + (eta   * wing_twist_ratio)                     # twist at center local chord 
                
                xi_prime_a1  = xi_LE_a + np.cos(section_twist_a)*(xi_a1-xi_LE_a) + np.sin(section_twist_a)*(zeta_a1-zeta_LE_a)   # x coordinate transformation of top left corner
                xi_prime_ah  = xi_LE_a + np.cos(section_twist_a)*(xi_ah-xi_LE_a) + np.sin(section_twist_a)*(zeta_ah-zeta_LE_a)   # x coordinate transformation of bottom left corner
                xi_prime_a2  = xi_LE_a + np.cos(section_twist_a)*(xi_a2-xi_LE_a) + np.sin(section_twist_a)*(zeta_a2-zeta_LE_a)   # x coordinate transformation of bottom left corner
                xi_prime_ac  = xi_LE_a + np.cos(section_twist_a)*(xi_ac-xi_LE_a) + np.sin(section_twist_a)*(zeta_a2-zeta_LE_a)   # x coordinate transformation of bottom left corner of control point
                xi_prime_bc  = xi_LE_b + np.cos(section_twist_b)*(xi_bc-xi_LE_b) + np.sin(section_twist_b)*(zeta_b1-zeta_LE_b)   # x coordinate transformation of top right corner of control point                         
                xi_prime_b1  = xi_LE_b + np.cos(section_twist_b)*(xi_b1-xi_LE_b) + np.sin(section_twist_b)*(zeta_b1-zeta_LE_b)   # x coordinate transformation of top right corner 
                xi_prime_bh  = xi_LE_b + np.cos(section_twist_b)*(xi_bh-xi_LE_b) + np.sin(section_twist_b)*(zeta_bh-zeta_LE_b)   # x coordinate transformation of top right corner 
                xi_prime_b2  = xi_LE_b + np.cos(section_twist_b)*(xi_b2-xi_LE_b) + np.sin(section_twist_b)*(zeta_b2-zeta_LE_b)   # x coordinate transformation of botton right corner 
                xi_prime     = xi_LE   + np.cos(section_twist)  *(xi_c-xi_LE)    + np.sin(section_twist)*(zeta-zeta_LE)          # x coordinate transformation of control point
                xi_prime_ch  = xi_LE   + np.cos(section_twist)  *(xi_ch-xi_LE)   + np.sin(section_twist)*(zeta_ch-zeta_LE)       # x coordinate transformation of center of horeshoe vortex 
                
                zeta_prime_a1  = zeta_LE_a - np.sin(section_twist_a)*(xi_a1-xi_LE_a) + np.cos(section_twist_a)*(zeta_a1-zeta_LE_a) # z coordinate transformation of top left corner
                zeta_prime_ah  = zeta_LE_a - np.sin(section_twist_a)*(xi_ah-xi_LE_a) + np.cos(section_twist_a)*(zeta_ah-zeta_LE_a) # z coordinate transformation of bottom left corner
                zeta_prime_a2  = zeta_LE_a - np.sin(section_twist_a)*(xi_a2-xi_LE_a) + np.cos(section_twist_a)*(zeta_a2-zeta_LE_a) # z coordinate transformation of bottom left corner
                zeta_prime_ac  = zeta_LE_a - np.sin(section_twist_a)*(xi_ac-xi_LE_a) + np.cos(section_twist_a)*(zeta_ac-zeta_LE_a) # z coordinate transformation of bottom left corner
                zeta_prime_bc  = zeta_LE_b - np.sin(section_twist_b)*(xi_bc-xi_LE_b) + np.cos(section_twist_b)*(zeta_bc-zeta_LE_b) # z coordinate transformation of top right corner                         
                zeta_prime_b1  = zeta_LE_b - np.sin(section_twist_b)*(xi_b1-xi_LE_b) + np.cos(section_twist_b)*(zeta_b1-zeta_LE_b) # z coordinate transformation of top right corner 
                zeta_prime_bh  = zeta_LE_b - np.sin(section_twist_b)*(xi_bh-xi_LE_b) + np.cos(section_twist_b)*(zeta_bh-zeta_LE_b) # z coordinate transformation of top right corner 
                zeta_prime_b2  = zeta_LE_b - np.sin(section_twist_b)*(xi_b2-xi_LE_b) + np.cos(section_twist_b)*(zeta_b2-zeta_LE_b) # z coordinate transformation of botton right corner 
                zeta_prime     = zeta_LE   - np.sin(section_twist)  *(xi_c-xi_LE)    + np.cos(-section_twist) *(zeta-zeta_LE)      # z coordinate transformation of control point
                zeta_prime_ch  = zeta_LE   - np.sin(section_twist)  *(xi_ch-xi_LE)   + np.cos(-section_twist) *(zeta_ch-zeta_LE)   # z coordinate transformation of center of horseshoe
                           
                # ** TO DO ** Get flap/aileron locations and deflection
                
                # store coordinates of panels, horseshoeces vortices and control points relative to wing root 
                if vertical_wing:
                    xa1[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_a1 
                    za1[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_a[idx_y]
                    ya1[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_a1
                    xa2[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_a2
                    za2[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_a[idx_y]
                    ya2[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_a2
                     
                    xb1[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_b1 
                    zb1[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_b[idx_y]
                    yb1[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_b1
                    xb2[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_b2 
                    zb2[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_b[idx_y]                        
                    yb2[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_b2 
             
                    xah[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_ah
                    zah[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_a[idx_y]
                    yah[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_ah                    
                    xbh[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_bh 
                    zbh[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_b[idx_y]
                    ybh[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_bh
                      
                    xch[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_ch
                    zch[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*(y_b[idx_y] - delta_y/2)                   
                    ych[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_ch
             
                    xc [idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime 
                    zc [idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*(y_b[idx_y] - delta_y/2) 
                    yc [idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime 
                
                    xac[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_ac 
                    zac[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_a[idx_y]
                    yac[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_ac
                    xbc[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_bc
                    zbc[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_b[idx_y]                            
                    ybc[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_bc                        
                     
                else: 
                    xa1[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_a1 
                    ya1[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_a[idx_y]
                    za1[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_a1
                    xa2[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_a2
                    ya2[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_a[idx_y]
                    za2[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_a2
                        
                    xb1[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_b1 
                    yb1[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_b[idx_y]
                    zb1[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_b1
                    yb2[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_b[idx_y]
                    xb2[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_b2 
                    zb2[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_b2 
                       
                    xah[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_ah
                    yah[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_a[idx_y]
                    zah[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_ah                    
                    xbh[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_bh 
                    ybh[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_b[idx_y]
                    zbh[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_bh
                          
                    xch[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_ch
                    ych[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*(y_b[idx_y] - delta_y[idx_y]/2)                   
                    zch[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_ch
                        
                    xc [idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime 
                    yc [idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*(y_b[idx_y] - delta_y[idx_y]/2) 
                    zc [idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime 
                          
                    xac[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_ac 
                    yac[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_a[idx_y]
                    zac[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_ac
                    xbc[idx_y*n_cw:(idx_y+1)*n_cw] = xi_prime_bc
                    ybc[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*y_b[idx_y]                            
                    zbc[idx_y*n_cw:(idx_y+1)*n_cw] = zeta_prime_bc                  
                
                cs_w[idx_y] = wing_chord_section
                                                                     
        # adjusting coordinate axis so reference point is at the nose of the aircraft
        xah = xah + wing_origin[0] # x coordinate of left corner of bound vortex 
        yah = yah + wing_origin[1] # y coordinate of left corner of bound vortex 
        zah = zah + wing_origin[2] # z coordinate of left corner of bound vortex 
        xbh = xbh + wing_origin[0] # x coordinate of right corner of bound vortex 
        ybh = ybh + wing_origin[1] # y coordinate of right corner of bound vortex 
        zbh = zbh + wing_origin[2] # z coordinate of right corner of bound vortex 
        xch = xch + wing_origin[0] # x coordinate of center of bound vortex on panel
        ych = ych + wing_origin[1] # y coordinate of center of bound vortex on panel
        zch = zch + wing_origin[2] # z coordinate of center of bound vortex on panel  
        
        xa1 = xa1 + wing_origin[0] # x coordinate of top left corner of panel
        ya1 = ya1 + wing_origin[1] # y coordinate of bottom left corner of panel
        za1 = za1 + wing_origin[2] # z coordinate of top left corner of panel
        xa2 = xa2 + wing_origin[0] # x coordinate of bottom left corner of panel
        ya2 = ya2 + wing_origin[1] # x coordinate of bottom left corner of panel
        za2 = za2 + wing_origin[2] # z coordinate of bottom left corner of panel  
        
        xb1 = xb1 + wing_origin[0] # x coordinate of top right corner of panel  
        yb1 = yb1 + wing_origin[1] # y coordinate of top right corner of panel 
        zb1 = zb1 + wing_origin[2] # z coordinate of top right corner of panel 
        xb2 = xb2 + wing_origin[0] # x coordinate of bottom rightcorner of panel 
        yb2 = yb2 + wing_origin[1] # y coordinate of bottom rightcorner of panel 
        zb2 = zb2 + wing_origin[2] # z coordinate of bottom right corner of panel                   
        
        xac = xac + wing_origin[0]  # x coordinate of control points on panel
        yac = yac + wing_origin[1]  # y coordinate of control points on panel
        zac = zac + wing_origin[2]  # z coordinate of control points on panel
        xbc = xbc + wing_origin[0]  # x coordinate of control points on panel
        ybc = ybc + wing_origin[1]  # y coordinate of control points on panel
        zbc = zbc + wing_origin[2]  # z coordinate of control points on panel
        
        xc  = xc + wing_origin[0]  # x coordinate of control points on panel
        yc  = yc + wing_origin[1]  # y coordinate of control points on panel
        zc  = zc + wing_origin[2]  # y coordinate of control points on panel
        
        # if symmetry, store points of mirrored wing 
        n_w += 1
        if sym_para is True :
            n_w += 1
            cs_w = np.concatenate([cs_w,cs_w])
            xah = np.concatenate([xah,xah])
            yah = np.concatenate([yah,-yah])
            zah = np.concatenate([zah,zah])
            xbh = np.concatenate([xbh,xbh])
            ybh = np.concatenate([ybh,-ybh])
            zbh = np.concatenate([zbh,zbh])
            xch = np.concatenate([xch,xch])
            ych = np.concatenate([ych,-ych])
            zch = np.concatenate([zch,zch])
                                         
            xa1 = np.concatenate([xa1,xa1])
            ya1 = np.concatenate([ya1,-ya1])
            za1 = np.concatenate([za1,za1])
            xa2 = np.concatenate([xa2,xa2])
            ya2 = np.concatenate([ya2,-ya2])
            za2 = np.concatenate([za2,za2])
                                      
            xb1 = np.concatenate([xb1,xb1])
            yb1 = np.concatenate([yb1,-yb1])    
            zb1 = np.concatenate([zb1,zb1])
            xb2 = np.concatenate([xb2,xb2])
            yb2 = np.concatenate([yb2,-yb2])            
            zb2 = np.concatenate([zb2,zb2])
                                      
            xac = np.concatenate([xac ,xac ])
            yac = np.concatenate([yac ,-yac ])
            zac = np.concatenate([zac ,zac ])            
            xbc = np.concatenate([xbc ,xbc ])
            ybc = np.concatenate([ybc ,-ybc ])
            zbc = np.concatenate([zbc ,zbc ])
            xc  = np.concatenate([xc ,xc ])
            yc  = np.concatenate([yc ,-yc])
            zc  = np.concatenate([zc ,zc ])
        
        n_cp += len(xch)        
        
        # ---------------------------------------------------------------------------------------
        # STEP 7: Store wing in vehicle vector
        # ---------------------------------------------------------------------------------------       
        VD.XAH  = np.append(VD.XAH,xah)
        VD.YAH  = np.append(VD.YAH,yah)
        VD.ZAH  = np.append(VD.ZAH,zah)
        VD.XBH  = np.append(VD.XBH,xbh)
        VD.YBH  = np.append(VD.YBH,ybh)
        VD.ZBH  = np.append(VD.ZBH,zbh)
        VD.XCH  = np.append(VD.XCH,xch)
        VD.YCH  = np.append(VD.YCH,ych)
        VD.ZCH  = np.append(VD.ZCH,zch)            
        VD.XA1  = np.append(VD.XA1,xa1)
        VD.YA1  = np.append(VD.YA1,ya1)
        VD.ZA1  = np.append(VD.ZA1,za1)
        VD.XA2  = np.append(VD.XA2,xa2)
        VD.YA2  = np.append(VD.YA2,ya2)
        VD.ZA2  = np.append(VD.ZA2,za2)        
        VD.XB1  = np.append(VD.XB1,xb1)
        VD.YB1  = np.append(VD.YB1,yb1)
        VD.ZB1  = np.append(VD.ZB1,zb1)
        VD.XB2  = np.append(VD.XB2,xb2)                
        VD.YB2  = np.append(VD.YB2,yb2)        
        VD.ZB2  = np.append(VD.ZB2,zb2)        
        VD.XAC  = np.append(VD.XAC,xac)
        VD.YAC  = np.append(VD.YAC,yac) 
        VD.ZAC  = np.append(VD.ZAC,zac) 
        VD.XBC  = np.append(VD.XBC,xbc)
        VD.YBC  = np.append(VD.YBC,ybc) 
        VD.ZBC  = np.append(VD.ZBC,zbc)  
        VD.XC   = np.append(VD.XC ,xc)
        VD.YC   = np.append(VD.YC ,yc)
        VD.ZC   = np.append(VD.ZC ,zc)  
        VD.CS   = np.append(VD.CS,cs_w)        
        
    # ---------------------------------------------------------------------------------------
    # STEP 8: Unpack aircraft fus geometry 
    # --------------------------------------------------------------------------------------- 
    fus_areas = [] # fus areas     
    
    for fus in geometry.fuselages:  
        fhs_xa1 = np.zeros(n_cw*n_sw)
        fhs_ya1 = np.zeros(n_cw*n_sw)
        fhs_za1 = np.zeros(n_cw*n_sw)
        fhs_xa2 = np.zeros(n_cw*n_sw)
        fhs_ya2 = np.zeros(n_cw*n_sw)
        fhs_za2 = np.zeros(n_cw*n_sw)
        fhs_xb1 = np.zeros(n_cw*n_sw)
        fhs_yb1 = np.zeros(n_cw*n_sw)
        fhs_zb1 = np.zeros(n_cw*n_sw)
        fhs_yb2 = np.zeros(n_cw*n_sw)
        fhs_xb2 = np.zeros(n_cw*n_sw)
        fhs_zb2 = np.zeros(n_cw*n_sw)
        fhs_xah = np.zeros(n_cw*n_sw)
        fhs_yah = np.zeros(n_cw*n_sw)
        fhs_zah = np.zeros(n_cw*n_sw)
        fhs_xbh = np.zeros(n_cw*n_sw)
        fhs_ybh = np.zeros(n_cw*n_sw)
        fhs_zbh = np.zeros(n_cw*n_sw)
        fhs_xch = np.zeros(n_cw*n_sw)
        fhs_ych = np.zeros(n_cw*n_sw)
        fhs_zch = np.zeros(n_cw*n_sw)
        fhs_xc  = np.zeros(n_cw*n_sw)
        fhs_yc  = np.zeros(n_cw*n_sw)
        fhs_zc  = np.zeros(n_cw*n_sw)
        fhs_xac = np.zeros(n_cw*n_sw)
        fhs_yac = np.zeros(n_cw*n_sw)
        fhs_zac = np.zeros(n_cw*n_sw)
        fhs_xbc = np.zeros(n_cw*n_sw)
        fhs_ybc = np.zeros(n_cw*n_sw)
        fhs_zbc = np.zeros(n_cw*n_sw)
           
        fvs_xa1 = np.zeros(n_cw*n_sw)
        fvs_za1 = np.zeros(n_cw*n_sw)
        fvs_ya1 = np.zeros(n_cw*n_sw)
        fvs_xa2 = np.zeros(n_cw*n_sw)
        fvs_za2 = np.zeros(n_cw*n_sw)
        fvs_ya2 = np.zeros(n_cw*n_sw)
        fvs_xb1 = np.zeros(n_cw*n_sw)
        fvs_zb1 = np.zeros(n_cw*n_sw)
        fvs_yb1 = np.zeros(n_cw*n_sw)
        fvs_xb2 = np.zeros(n_cw*n_sw)
        fvs_zb2 = np.zeros(n_cw*n_sw)
        fvs_yb2 = np.zeros(n_cw*n_sw)
        fvs_xah = np.zeros(n_cw*n_sw)
        fvs_zah = np.zeros(n_cw*n_sw)
        fvs_yah = np.zeros(n_cw*n_sw)
        fvs_xbh = np.zeros(n_cw*n_sw)
        fvs_zbh = np.zeros(n_cw*n_sw)
        fvs_ybh = np.zeros(n_cw*n_sw)
        fvs_xch = np.zeros(n_cw*n_sw)
        fvs_zch = np.zeros(n_cw*n_sw)
        fvs_ych = np.zeros(n_cw*n_sw)
        fvs_xc  = np.zeros(n_cw*n_sw)
        fvs_zc  = np.zeros(n_cw*n_sw)
        fvs_yc  = np.zeros(n_cw*n_sw)
        fvs_xac = np.zeros(n_cw*n_sw)
        fvs_zac = np.zeros(n_cw*n_sw)
        fvs_yac = np.zeros(n_cw*n_sw)
        fvs_xbc = np.zeros(n_cw*n_sw)
        fvs_zbc = np.zeros(n_cw*n_sw)
        fvs_ybc = np.zeros(n_cw*n_sw)
    
        n_w += 4
        fus_areas = np.append(fus_areas,fus.areas.side_projected )
        semispan_h = fus.width * 0.5  
        semispan_v = fus.heights.maximum * 0.5
        origin     = fus.origin[0]
                      
        # Compute the curvature of the nose/tail given fineness ratio. Curvature is derived from general quadratic equation
        # This method relates the fineness ratio to the quadratic curve formula via a spline fit interpolation
        vec1 = [2 , 1.5, 1.2 , 1]
        vec2 = [1  ,1.57 , 3.2,  8]
        x = np.linspace(0,1,4)
        fus_nose_curvature =  np.interp(np.interp(fus.fineness.nose,vec2,x), x , vec1)
        fus_tail_curvature =  np.interp(np.interp(fus.fineness.tail,vec2,x), x , vec1) 
    
        # Horizontal Sections of fuselage
        fhs = Data()        
        fhs.origin        = np.zeros((n_sw,3))        
        fhs.chord         = np.zeros((n_sw))         
        fhs.sweep         = np.zeros((n_sw))     
    
        fvs = Data()
        fvs.origin        = np.zeros((n_sw,3))
        fvs.chord         = np.zeros((n_sw)) 
        fvs.sweep         = np.zeros((n_sw)) 
    
        si  = np.arange(1,((n_sw*2)+2))
        spacing = np.cos((2*si - 1)/(2*len(si))*np.pi)     
        h_array = semispan_h*spacing[0:int((len(si)+1)/2)][::-1]  
        v_array = semispan_v*spacing[0:int((len(si)+1)/2)][::-1]  
        
        for i in range(n_sw): 
            fhs_cabin_length  = fus.lengths.total - (fus.lengths.nose + fus.lengths.tail)
            fhs.nose_length   = ((1 - ((abs(h_array[i]/semispan_h))**fus_nose_curvature ))**(1/fus_nose_curvature))*fus.lengths.nose
            fhs.tail_length   = ((1 - ((abs(h_array[i]/semispan_h))**fus_tail_curvature ))**(1/fus_tail_curvature))*fus.lengths.tail
            fhs.nose_origin   = fus.lengths.nose - fhs.nose_length 
            fhs.origin[i][:]  = np.array([origin[0] + fhs.nose_origin , origin[1] + h_array[i], origin[2]])
            fhs.chord[i]      = fhs_cabin_length + fhs.nose_length + fhs.tail_length          
            
            
            fvs_cabin_length  = fus.lengths.total - (fus.lengths.nose + fus.lengths.tail)
            fvs.nose_length   = ((1 - ((abs(v_array[i]/semispan_v))**fus_nose_curvature ))**(1/fus_nose_curvature))*fus.lengths.nose
            fvs.tail_length   = ((1 - ((abs(v_array[i]/semispan_v))**fus_tail_curvature ))**(1/fus_tail_curvature))*fus.lengths.tail
            fvs.nose_origin   = fus.lengths.nose - fvs.nose_length 
            fvs.origin[i][:]  = np.array([origin[0] + fvs.nose_origin , origin[1] , origin[2]+  v_array[i]])
            fvs.chord[i]      = fvs_cabin_length + fvs.nose_length + fvs.tail_length
        
        fhs.sweep[:]      = np.concatenate([np.arctan((fhs.origin[:,0][1:] - fhs.origin[:,0][:-1])/(fhs.origin[:,1][1:]  - fhs.origin[:,1][:-1])) ,np.zeros(1)])
        fvs.sweep[:]      = np.concatenate([np.arctan((fvs.origin[:,0][1:] - fvs.origin[:,0][:-1])/(fvs.origin[:,2][1:]  - fvs.origin[:,2][:-1])) ,np.zeros(1)])
        
        print(fhs.origin)     
        print(fhs.chord)    
        # ---------------------------------------------------------------------------------------
        # STEP 9: Define coordinates of panels horseshoe vortices and control points np.concatenate([np.arctan((fhs.origin[:,0][1:] - fhs.origin[:,0][:-1])/(fhs.origin[:,1][1:]  - fhs.origin[:,1][:-1])) ,0])
        # ---------------------------------------------------------------------------------------        
        fhs_eta_a = h_array[:-1] 
        fhs_eta_b = h_array[1:]            
        fhs_del_y = h_array[1:] - h_array[:-1]
        fhs_eta   = h_array[1:] - fhs_del_y/2
        
        fvs_eta_a = v_array[:-1] 
        fvs_eta_b = v_array[1:]                  
        fvs_del_y = v_array[1:] - v_array[:-1]
        fvs_eta   = v_array[1:] - fvs_del_y/2 
        
        fhs_cs = np.concatenate([fhs.chord,fhs.chord])
        fvs_cs = np.concatenate([fvs.chord,fvs.chord])
        
        # define coordinates of horseshoe vortices and control points       
        for idx_y in range(n_sw-1):  
            idx_x = np.arange(n_cw)
            # fuselage horizontal section             
        
            delta_x_a = fhs.chord[idx_y]/n_cw      
            delta_x_b = fhs.chord[idx_y + 1]/n_cw    
            delta_x   = (fhs.chord[idx_y]+fhs.chord[idx_y + 1])/(2*n_cw)                                   
        
            fhs_xi_a1 = fhs.origin[idx_y][0] + delta_x_a*idx_x                  # x coordinate of top left corner of panel
            fhs_xi_ah = fhs.origin[idx_y][0] + delta_x_a*idx_x + delta_x_a*0.25 # x coordinate of left corner of panel
            fhs_xi_a2 = fhs.origin[idx_y][0] + delta_x_a*idx_x + delta_x_a      # x coordinate of bottom left corner of bound vortex 
            fhs_xi_ac = fhs.origin[idx_y][0] + delta_x_a*idx_x + delta_x_a*0.75 # x coordinate of bottom left corner of control point vortex  
            fhs_xi_b1 = fhs.origin[idx_y][0] + delta_x_b*idx_x                  # x coordinate of top right corner of panel      
            fhs_xi_bh = fhs.origin[idx_y][0] + delta_x_b*idx_x + delta_x_b*0.25 # x coordinate of right corner of bound vortex         
            fhs_xi_b2 = fhs.origin[idx_y][0] + delta_x_b*idx_x + delta_x_b      # x coordinate of bottom right corner of panel
            fhs_xi_bc = fhs.origin[idx_y][0] + delta_x_b*idx_x + delta_x_b*0.75 # x coordinate of bottom right corner of control point vortex         
            fhs_xi_c  = fhs.origin[idx_y][0] + delta_x  *idx_x + delta_x*0.75   # x coordinate three-quarter chord control point for each panel
            fhs_xi_ch = fhs.origin[idx_y][0] + delta_x  *idx_x + delta_x*0.25   # x coordinate center of bound vortex of each panel 
            
            fhs_xa1[idx_y*n_cw:(idx_y+1)*n_cw] = fhs_xi_a1                       + fus.origin[0][0]  
            fhs_ya1[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fhs_eta_a[idx_y]  + fus.origin[0][1]  
            fhs_za1[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                  + fus.origin[0][2]
            fhs_xa2[idx_y*n_cw:(idx_y+1)*n_cw] = fhs_xi_a2                       + fus.origin[0][0]  
            fhs_ya2[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fhs_eta_a[idx_y]  + fus.origin[0][1] 
            fhs_za2[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                  + fus.origin[0][2]      
            fhs_xb1[idx_y*n_cw:(idx_y+1)*n_cw] = fhs_xi_b1                       + fus.origin[0][0]  
            fhs_yb1[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fhs_eta_b[idx_y]  + fus.origin[0][1] 
            fhs_zb1[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                  + fus.origin[0][2]
            fhs_yb2[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fhs_eta_b[idx_y]  + fus.origin[0][1]  
            fhs_xb2[idx_y*n_cw:(idx_y+1)*n_cw] = fhs_xi_b2                       + fus.origin[0][0] 
            fhs_zb2[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                  + fus.origin[0][2]       
            fhs_xah[idx_y*n_cw:(idx_y+1)*n_cw] = fhs_xi_ah                       + fus.origin[0][0]   
            fhs_yah[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fhs_eta_a[idx_y]  + fus.origin[0][1]  
            fhs_zah[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                  + fus.origin[0][2]             
            fhs_xbh[idx_y*n_cw:(idx_y+1)*n_cw] = fhs_xi_bh                       + fus.origin[0][0] 
            fhs_ybh[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fhs_eta_b[idx_y]  + fus.origin[0][1]  
            fhs_zbh[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                  + fus.origin[0][2]    
            fhs_xch[idx_y*n_cw:(idx_y+1)*n_cw] = fhs_xi_ch                       + fus.origin[0][0]  
            fhs_ych[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fhs_eta[idx_y]    + fus.origin[0][1]                
            fhs_zch[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                  + fus.origin[0][2]     
            fhs_xc [idx_y*n_cw:(idx_y+1)*n_cw] = fhs_xi_c                        + fus.origin[0][0]  
            fhs_yc [idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fhs_eta[idx_y]    + fus.origin[0][1]  
            fhs_zc [idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                  + fus.origin[0][2]       
            fhs_xac[idx_y*n_cw:(idx_y+1)*n_cw] = fhs_xi_ac                       + fus.origin[0][0]  
            fhs_yac[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fhs_eta_a[idx_y]  + fus.origin[0][1]
            fhs_zac[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                  + fus.origin[0][2]
            fhs_xbc[idx_y*n_cw:(idx_y+1)*n_cw] = fhs_xi_bc                       + fus.origin[0][0]  
            fhs_ybc[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fhs_eta_b[idx_y]  + fus.origin[0][1]                             
            fhs_zbc[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                  + fus.origin[0][2]                     
            
            # fuselage vertical section             
            fvs_chord_section = fvs.chord[idx_y]  
            
            delta_x_a = fvs.chord[idx_y]/n_cw      
            delta_x_b = fvs.chord[idx_y + 1]/n_cw    
            delta_x   = (fvs.chord[idx_y]+fvs.chord[idx_y + 1])/(2*n_cw)                                            
        
            fvs_xi_a1 = fvs.origin[idx_y][0] + delta_x_a*idx_x                         # z coordinate of top left corner of panel
            fvs_xi_ah = fvs.origin[idx_y][0] + delta_x_a*idx_x + delta_x_a*0.25 # z coordinate of left corner of panel
            fvs_xi_a2 = fvs.origin[idx_y][0] + delta_x_a*idx_x + delta_x_a      # z coordinate of bottom left corner of bound vortex 
            fvs_xi_ac = fvs.origin[idx_y][0] + delta_x_a*idx_x + delta_x_a*0.75 # z coordinate of bottom left corner of control point vortex  
            fvs_xi_b1 = fvs.origin[idx_y][0] + delta_x_b*idx_x                  # z coordinate of top right corner of panel      
            fvs_xi_bh = fvs.origin[idx_y][0] + delta_x_b*idx_x + delta_x_b*0.25 # z coordinate of right corner of bound vortex         
            fvs_xi_b2 = fvs.origin[idx_y][0] + delta_x_b*idx_x + delta_x_b      # z coordinate of bottom right corner of panel
            fvs_xi_bc = fvs.origin[idx_y][0] + delta_x_b*idx_x + delta_x_b*0.75 # z coordinate of bottom right corner of control point vortex         
            fvs_xi_c  = fvs.origin[idx_y][0] + delta_x  *idx_x   + delta_x*0.75   # z coordinate three-quarter chord control point for each panel
            fvs_xi_ch = fvs.origin[idx_y][0] + delta_x  *idx_x   + delta_x*0.25   # z coordinate center of bound vortex of each panel 
            
           
            fvs_xa1[idx_y*n_cw:(idx_y+1)*n_cw] = fvs_xi_a1                      + fus.origin[0][0]  
            fvs_za1[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fvs_eta_a[idx_y] + fus.origin[0][2]  
            fvs_ya1[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                 + fus.origin[0][1]
            fvs_xa2[idx_y*n_cw:(idx_y+1)*n_cw] = fvs_xi_a2                      + fus.origin[0][0]  
            fvs_za2[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fvs_eta_a[idx_y] + fus.origin[0][2] 
            fvs_ya2[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                 + fus.origin[0][1]      
            fvs_xb1[idx_y*n_cw:(idx_y+1)*n_cw] = fvs_xi_b1                      + fus.origin[0][0]  
            fvs_zb1[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fvs_eta_b[idx_y] + fus.origin[0][2] 
            fvs_yb1[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                 + fus.origin[0][1]
            fvs_xb2[idx_y*n_cw:(idx_y+1)*n_cw] = fvs_xi_b2                      + fus.origin[0][0]  
            fvs_zb2[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fvs_eta_b[idx_y] + fus.origin[0][2]    
            fvs_yb2[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                 + fus.origin[0][1]       
            fvs_xah[idx_y*n_cw:(idx_y+1)*n_cw] = fvs_xi_ah                      + fus.origin[0][0]   
            fvs_zah[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fvs_eta_a[idx_y] + fus.origin[0][2]  
            fvs_yah[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                 + fus.origin[0][1]        
            fvs_xbh[idx_y*n_cw:(idx_y+1)*n_cw] = fvs_xi_bh                      + fus.origin[0][0] 
            fvs_zbh[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fvs_eta_b[idx_y] + fus.origin[0][2]  
            fvs_ybh[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                 + fus.origin[0][1]    
            fvs_xch[idx_y*n_cw:(idx_y+1)*n_cw] = fvs_xi_ch                      + fus.origin[0][0]  
            fvs_zch[idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fvs_eta[idx_y]   + fus.origin[0][2]                        
            fvs_ych[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                 + fus.origin[0][1]     
            fvs_xc [idx_y*n_cw:(idx_y+1)*n_cw] = fvs_xi_c                       + fus.origin[0][0]  
            fvs_zc [idx_y*n_cw:(idx_y+1)*n_cw] = np.ones(n_cw)*fvs_eta[idx_y]   + fus.origin[0][2]  
            fvs_yc [idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                 + fus.origin[0][1]       
            fvs_xac[idx_y*n_cw:(idx_y+1)*n_cw] = fvs_xi_ac                      + fus.origin[0][0]  
            fvs_zac[idx_y*n_cw:(idx_y+1)*n_cw] = fvs_eta_a[idx_y]               + fus.origin[0][2]
            fvs_yac[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                 + fus.origin[0][1]
            fvs_xbc[idx_y*n_cw:(idx_y+1)*n_cw] = fvs_xi_bc                      + fus.origin[0][0]  
            fvs_zbc[idx_y*n_cw:(idx_y+1)*n_cw] = fvs_eta_b[idx_y]               + fus.origin[0][2]               
            fvs_ybc[idx_y*n_cw:(idx_y+1)*n_cw] = np.zeros(n_cw)                 + fus.origin[0][1]        
        
    
        # store points of horizontal section of fuselage         
        fhs_xah = np.concatenate([fhs_xah, fhs_xah])
        fhs_yah = np.concatenate([fhs_yah,-fhs_yah])
        fhs_zah = np.concatenate([fhs_zah, fhs_zah])
        fhs_xbh = np.concatenate([fhs_xbh, fhs_xbh])
        fhs_ybh = np.concatenate([fhs_ybh,-fhs_ybh])
        fhs_zbh = np.concatenate([fhs_zbh, fhs_zbh])
        fhs_xch = np.concatenate([fhs_xch, fhs_xch])
        fhs_ych = np.concatenate([fhs_ych,-fhs_ych])
        fhs_zch = np.concatenate([fhs_zch, fhs_zch])
        fhs_xa1 = np.concatenate([fhs_xa1, fhs_xa1])
        fhs_ya1 = np.concatenate([fhs_ya1,-fhs_ya1])
        fhs_za1 = np.concatenate([fhs_za1, fhs_za1])
        fhs_xa2 = np.concatenate([fhs_xa2, fhs_xa2])
        fhs_ya2 = np.concatenate([fhs_ya2,-fhs_ya2])
        fhs_za2 = np.concatenate([fhs_za2, fhs_za2])
        fhs_xb1 = np.concatenate([fhs_xb1, fhs_xb1])
        fhs_yb1 = np.concatenate([fhs_yb1,-fhs_yb1])    
        fhs_zb1 = np.concatenate([fhs_zb1, fhs_zb1])
        fhs_xb2 = np.concatenate([fhs_xb2, fhs_xb2])
        fhs_yb2 = np.concatenate([fhs_yb2,-fhs_yb2])            
        fhs_zb2 = np.concatenate([fhs_zb2, fhs_zb2])
        fhs_xac = np.concatenate([fhs_xac, fhs_xac])
        fhs_yac = np.concatenate([fhs_yac,-fhs_yac])
        fhs_zac = np.concatenate([fhs_zac, fhs_zac])            
        fhs_xbc = np.concatenate([fhs_xbc, fhs_xbc])
        fhs_ybc = np.concatenate([fhs_ybc,-fhs_ybc])
        fhs_zbc = np.concatenate([fhs_zbc, fhs_zbc])
        fhs_xc  = np.concatenate([fhs_xc , fhs_xc ])
        fhs_yc  = np.concatenate([fhs_yc ,-fhs_yc])
        fhs_zc  = np.concatenate([fhs_zc , fhs_zc ])            
     
        
        # store points of vertical section of fuselage 
        fvs_xah = np.concatenate([fvs_xah, fvs_xah])
        fvs_yah = np.concatenate([fvs_yah, fvs_yah])
        fvs_zah = np.concatenate([fvs_zah,-fvs_zah])
        fvs_xbh = np.concatenate([fvs_xbh, fvs_xbh])
        fvs_ybh = np.concatenate([fvs_ybh, fvs_ybh])
        fvs_zbh = np.concatenate([fvs_zbh,-fvs_zbh])
        fvs_xch = np.concatenate([fvs_xch, fvs_xch])
        fvs_ych = np.concatenate([fvs_ych, fvs_ych])
        fvs_zch = np.concatenate([fvs_zch,-fvs_zch])
        fvs_xa1 = np.concatenate([fvs_xa1, fvs_xa1])
        fvs_ya1 = np.concatenate([fvs_ya1, fvs_ya1])
        fvs_za1 = np.concatenate([fvs_za1,-fvs_za1])
        fvs_xa2 = np.concatenate([fvs_xa2, fvs_xa2])
        fvs_ya2 = np.concatenate([fvs_ya2, fvs_ya2])
        fvs_za2 = np.concatenate([fvs_za2,-fvs_za2])
        fvs_xb1 = np.concatenate([fvs_xb1, fvs_xb1])
        fvs_yb1 = np.concatenate([fvs_yb1, fvs_yb1])    
        fvs_zb1 = np.concatenate([fvs_zb1,-fvs_zb1])
        fvs_xb2 = np.concatenate([fvs_xb2, fvs_xb2])
        fvs_yb2 = np.concatenate([fvs_yb2, fvs_yb2])            
        fvs_zb2 = np.concatenate([fvs_zb2,-fvs_zb2])
        fvs_xac = np.concatenate([fvs_xac, fvs_xac ])
        fvs_yac = np.concatenate([fvs_yac, fvs_yac ])
        fvs_zac = np.concatenate([fvs_zac,-fvs_zac ])            
        fvs_xbc = np.concatenate([fvs_xbc, fvs_xbc ])
        fvs_ybc = np.concatenate([fvs_ybc, fvs_ybc ])
        fvs_zbc = np.concatenate([fvs_zbc,-fvs_zbc ])
        fvs_xc  = np.concatenate([fvs_xc , fvs_xc ])
        fvs_yc  = np.concatenate([fvs_yc , fvs_yc])
        fvs_zc  = np.concatenate([fvs_zc ,-fvs_zc ])
        
        n_cp += 4*len(fhs_xch)
        
        # ---------------------------------------------------------------------------------------
        # STEP  : Store fus in vehicle vector
        # ---------------------------------------------------------------------------------------       
        VD.XAH  = np.append(VD.XAH,fhs_xah)
        VD.YAH  = np.append(VD.YAH,fhs_yah)
        VD.ZAH  = np.append(VD.ZAH,fhs_zah)
        VD.XBH  = np.append(VD.XBH,fhs_xbh)
        VD.YBH  = np.append(VD.YBH,fhs_ybh)
        VD.ZBH  = np.append(VD.ZBH,fhs_zbh)
        VD.XCH  = np.append(VD.XCH,fhs_xch)
        VD.YCH  = np.append(VD.YCH,fhs_ych)
        VD.ZCH  = np.append(VD.ZCH,fhs_zch)     
        VD.XA1  = np.append(VD.XA1,fhs_xa1)
        VD.YA1  = np.append(VD.YA1,fhs_ya1)
        VD.ZA1  = np.append(VD.ZA1,fhs_za1)
        VD.XA2  = np.append(VD.XA2,fhs_xa2)
        VD.YA2  = np.append(VD.YA2,fhs_ya2)
        VD.ZA2  = np.append(VD.ZA2,fhs_za2)    
        VD.XB1  = np.append(VD.XB1,fhs_xb1)
        VD.YB1  = np.append(VD.YB1,fhs_yb1)
        VD.ZB1  = np.append(VD.ZB1,fhs_zb1)
        VD.XB2  = np.append(VD.XB2,fhs_xb2)                
        VD.YB2  = np.append(VD.YB2,fhs_yb2)        
        VD.ZB2  = np.append(VD.ZB2,fhs_zb2)    
        VD.XAC  = np.append(VD.XAC,fhs_xac)
        VD.YAC  = np.append(VD.YAC,fhs_yac) 
        VD.ZAC  = np.append(VD.ZAC,fhs_zac) 
        VD.XBC  = np.append(VD.XBC,fhs_xbc)
        VD.YBC  = np.append(VD.YBC,fhs_ybc) 
        VD.ZBC  = np.append(VD.ZBC,fhs_zbc)  
        VD.XC   = np.append(VD.XC ,fhs_xc)
        VD.YC   = np.append(VD.YC ,fhs_yc)
        VD.ZC   = np.append(VD.ZC ,fhs_zc)  
        VD.CS   = np.append(VD.CS ,fhs_cs) 
                          
        VD.XAH  = np.append(VD.XAH,fvs_xah)
        VD.YAH  = np.append(VD.YAH,fvs_yah)
        VD.ZAH  = np.append(VD.ZAH,fvs_zah)
        VD.XBH  = np.append(VD.XBH,fvs_xbh)
        VD.YBH  = np.append(VD.YBH,fvs_ybh)
        VD.ZBH  = np.append(VD.ZBH,fvs_zbh)
        VD.XCH  = np.append(VD.XCH,fvs_xch)
        VD.YCH  = np.append(VD.YCH,fvs_ych)
        VD.ZCH  = np.append(VD.ZCH,fvs_zch)     
        VD.XA1  = np.append(VD.XA1,fvs_xa1)
        VD.YA1  = np.append(VD.YA1,fvs_ya1)
        VD.ZA1  = np.append(VD.ZA1,fvs_za1)
        VD.XA2  = np.append(VD.XA2,fvs_xa2)
        VD.YA2  = np.append(VD.YA2,fvs_ya2)
        VD.ZA2  = np.append(VD.ZA2,fvs_za2)    
        VD.XB1  = np.append(VD.XB1,fvs_xb1)
        VD.YB1  = np.append(VD.YB1,fvs_yb1)
        VD.ZB1  = np.append(VD.ZB1,fvs_zb1)
        VD.XB2  = np.append(VD.XB2,fvs_xb2)                
        VD.YB2  = np.append(VD.YB2,fvs_yb2)        
        VD.ZB2  = np.append(VD.ZB2,fvs_zb2)    
        VD.XAC  = np.append(VD.XAC,fvs_xac)
        VD.YAC  = np.append(VD.YAC,fvs_yac) 
        VD.ZAC  = np.append(VD.ZAC,fvs_zac) 
        VD.XBC  = np.append(VD.XBC,fvs_xbc)
        VD.YBC  = np.append(VD.YBC,fvs_ybc) 
        VD.ZBC  = np.append(VD.ZBC,fvs_zbc)  
        VD.XC   = np.append(VD.XC ,fvs_xc)
        VD.YC   = np.append(VD.YC ,fvs_yc)
        VD.ZC   = np.append(VD.ZC ,fvs_zc)  
        VD.CS   = np.append(VD.CS ,fvs_cs)     
        
    VD.n_w  = n_w
    VD.n_cp = n_cp    
    VD.fus_areas = fus_areas
    VD.wing_areas = wing_areas    
    geometry.vortex_distribution = VD
    
    return VD 