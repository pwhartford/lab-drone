import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.cm as cm
from sklearn.model_selection import train_test_split
import pickle 
import matplotlib.ticker as ticker
COLORMAP = cm.get_cmap('Set1')
CAPSIZE = 2

#Constants 
rho_air = 1.225 #kg/m^3
mu_air = 1.789e-5 #Pa*s
nu_air = mu_air/rho_air

def learning_regression(x, y, n_trials = 500, order = 1):
    # Initialize coefficients:
    coeffs = np.zeros((n_trials, order+1))
    # a_s=np.zeros((n_trials,1)); b_s=np.zeros((n_trials,1))
   
    # Initialize Errors 
    E_in=np.zeros((n_trials,1)); E_out=np.zeros((n_trials,1))
    
    # Create the domain for the Regression Prediction
    x_reg=np.linspace(x.min(),x.max(),100)
    y_reg=np.zeros((x_reg.shape[0],n_trials))



    for j in range(0,n_trials):
        # Split randomly testing/training
        xs, xss, ys, yss = train_test_split(x,y, test_size=0.3)
        
        #Perform the fit over training
        z=np.polyfit(xs, ys, order)
       
        # Assign the results to vectors a_s and b_s
        coeffs[j,:] = z 

       
        # Compute a prediction and store results
        y_reg[:,j]=np.polyval(z,x_reg)
       
        # Root y_reg_mean Square Error in Training
        E_in[j]=np.linalg.norm(ys-np.polyval(z,xs))/np.sqrt(len(ys))
        
        # Root y_reg_mean Square Error in Testing
        E_out[j]=np.linalg.norm(yss-np.polyval(z,xss))/np.sqrt(len(yss))

    return x_reg, y_reg, E_in, E_out, coeffs

def plot_regression_results(x, y, x_reg, y_reg, E_out, coeffs, labels = ['',''], legend = None, fig = None, ax = None):
    # Compute the y_reg_mean and the STD of the prediction
    y_reg_mean=np.mean(y_reg,axis=1)

    i = 0
    for coeff in coeffs: 
        if i==0:
            y_reg_mean_2=coeff*x_reg**(coeffs.shape[0]-(i+1))
        else:
            y_reg_mean_2+=coeff*x_reg**(coeffs.shape[0]-(i+1))
        i+=1

    y_reg_std=np.std(y_reg,axis=1)

    Unc = E_out.mean()+1.96*y_reg_std
    # Unc = np.sqrt(E_out.mean()**2)+(y_reg_std*1.96/np.sqrt(x.shape[0]))
    
    if fig is None:
        fig = plt.figure() 
    
    if ax is None: 
        ax = plt.axes()

    ax.plot(x_reg, y_reg_mean_2, linestyle = 'dashed', color = 'k')   
    ax.fill_between(x_reg, y_reg_mean+Unc, y_reg_mean - Unc, color = COLORMAP(1), alpha=0.5)
   
    #Plot Markers
    ax.plot(x,y, marker = '.', linestyle = 'none', color = COLORMAP(0))
       
    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1])

    fig.tight_layout(pad=2)

    if legend is not None:
        ax.legend(legend)

    return fig, ax 
    

def load_hw_file(filepath):
    with open(filepath, 'rb') as hw_file:
        hw_data = pickle.load(hw_file)
        
    return np.array(hw_data[0]), np.array(hw_data[1]), hw_data




def plot_bl_profile(y, u, ax = plt.axes(), unc_u = 0.1, invert = False, invert_axis = False):
    Uinfty = np.max(u)

    if invert:
        delta = y[np.max(np.where(u>0.99*Uinfty))]
    else:
        delta = y[np.min(np.where(u>0.99*Uinfty))]

    y_delta = y/delta 

    unc = unc_u/Uinfty

    theoretical_y = np.linspace(y_delta.min(), y_delta.max(), 1000)
    theoretical = (theoretical_y)**(1/7)
    theoretical[np.where(theoretical>0.99)] = 1

    if invert_axis:
        ax.plot(theoretical_y, theoretical, linestyle = 'dashed', color = COLORMAP(1))
        ax.errorbar(y_delta, u/Uinfty, unc, color = COLORMAP(0), linestyle = 'none',  marker = '.', markersize = 3, ecolor = 'k', capsize = 1)

        ax.set_xlabel('$Y/\delta$')
        ax.set_ylabel('$U/U_\infty$')
    else:
        ax.plot(theoretical, theoretical_y, linestyle = 'dashed', color = COLORMAP(1))
        ax.errorbar(u/Uinfty, y_delta, xerr = unc, color = COLORMAP(0), linestyle = 'none',  marker = '.', markersize = 3, ecolor = 'k', capsize = CAPSIZE)

        ax.set_xlabel('$U/U_\infty$')
        ax.set_ylabel('$Y/\delta$')

    ax.legend(['Theoretical Profile', 'Experimental Data']) 

    ax.set_box_aspect(1)


    return ax 

def plot_log_profile(y, u, ax = plt.axes(), unc = 0.1,  plot_theoretical = True, marker = '.', set_legend = True, color = 0, error = True):
    Yplus, Uplus, Cf = bradshaw_method(y, u)
    Uinfty = u.max()

    unc_u = unc/Uinfty *np.sqrt(2/Cf)

    Yplus_theoretical = np.linspace(Yplus.min(), Yplus.max(), 10000)
    #Theoretical log law of the wall - 3 Different parts of the BL
    
    Uplus_theoretical = 5 + 2.44*np.log(Yplus_theoretical)
    Uplus_theoretical[np.where(Yplus_theoretical<30)] = -3.05 + 5.0*np.log(Yplus_theoretical[np.where(Yplus_theoretical<30)])
    Uplus_theoretical[np.where(Yplus_theoretical<5)] = Yplus_theoretical[np.where(Yplus_theoretical<5)]
       
    if plot_theoretical:
        ax.plot(Yplus_theoretical, Uplus_theoretical, linestyle = 'dashed', color = COLORMAP(1))
    
    if error:
        ax.errorbar(Yplus, Uplus, yerr = unc_u, linestyle = 'none', color = COLORMAP(color), marker = marker, markersize = 4, ecolor = 'k', capsize = CAPSIZE)
    
    else:
        ax.plot(Yplus, Uplus, linestyle = 'none', color = COLORMAP(color), marker = marker, markersize = 4)


    ax.set_xlabel('$Y^+$')
    ax.set_ylabel('$U^+$')

    ax.set_xscale('log')


    if set_legend:
        ax.legend(['Theoretical Log Law', 'Experimental Data'])

    ax.set_box_aspect(1)

    return ax

def compute_hw_vel(hw_e, coeffs):
    hw_vel = coeffs[0]*hw_e**4 + coeffs[1]*hw_e**3 + coeffs[2]*hw_e**2 + coeffs[3]*hw_e**1 + coeffs[4]

    # return hw_vel, hw_unc

    return hw_vel

# def compute_hw_uncertainty(hw_e, )


def plot_turb_intensity(y, u, ax = plt.axes(),  invert = True):
    Uinfty = np.max(np.mean(u,1))
    
    Yplus, Uplus, Cf = bradshaw_method(y, np.mean(u,1))
    TI = np.std(u, 1)/Uinfty

    epsilon_TI = 2/np.sqrt(2*u.shape[1])

    ax.errorbar(Yplus, TI*100, yerr = epsilon_TI, linestyle = 'dashed', marker = '.', markersize = 4, markerfacecolor = COLORMAP(0), markeredgecolor = COLORMAP(0), color = COLORMAP(1), ecolor = 'k', capsize = CAPSIZE)

    ax.set_ylabel('Turbulence Intensity $[\%]$')
    ax.set_xlabel('$Y^+$')

    ax.set_xscale('log')
    ax.set_box_aspect(1)

    return ax

def bradshaw_method(y, u):
    Uinfty = np.max(u)
    
    #Bradshaw for y+=100 
    #Find where U/uinfty - 1624*nu_air/(y*Uinfty) is smallest 
    difference_array = np.abs(u/Uinfty-1624*nu_air/(y*Uinfty))
    uinfty_index = np.where(difference_array==difference_array[np.isfinite(difference_array)].min())
    
    u_uinfty_star = u[uinfty_index]/Uinfty
        
    #Find Uplus and Yplus coordinates
    Cf = 2*(u_uinfty_star/ 16.24)**2

    Uplus = u/Uinfty *np.sqrt(2/Cf)
    Yplus = Uinfty *y* np.sqrt(Cf/2)/nu_air

    return Yplus, Uplus, Cf

def calculate_pressure_velocity(delta_p, coeffs, rho, epsilon_p_rand, epsilon_p_calib, epsilon_rho = 0):

    u = np.sqrt(2*((delta_p)*coeffs[0]+coeffs[1])/rho_air)

    epsilon_u = calculate_pressure_uncertainty(delta_p, rho, epsilon_p_rand, epsilon_p_calib, epsilon_rho)

    return u, epsilon_u

def calculate_pressure_uncertainty(delta_p, rho, epsilon_p_rand, epsilon_p_calib, epsilon_rho = 0): 
    epsilon_delta_p = np.sqrt(epsilon_p_rand**2 + epsilon_p_calib**2)

    du_dp = 1/2*np.sqrt(2/(rho*delta_p))
    du_drho = -1/2*np.sqrt(2*delta_p/rho**3)

    # epsilon_u = np.sqrt((du_dp*epsilon_delta_p)**2+(du_drho*epsilon_rho)**2)

    epsilon_u = du_dp*epsilon_delta_p

    return epsilon_u

def calculate_hw_uncertainty(u, ux, uy):
    u_mean = np.mean(u,1)

    epsilon_cal = np.interp(u_mean, ux, uy)

    epsilon_sigma = 1.96*np.std(u, 1)/np.sqrt(u.shape[1])
     
    epsilon_u = np.sqrt(epsilon_cal**2 + epsilon_sigma**2) 

    return epsilon_u