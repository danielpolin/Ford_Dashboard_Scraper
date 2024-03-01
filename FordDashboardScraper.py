#import stuff
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time,datetime,subprocess,numpy,sys, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import matplotlib.pyplot as plt

def Send_Email(message_subject, message_text, to_list, email_address, email_password):
    if len(to_list) > 0:
        msg = MIMEMultipart()
        msg['From']=email_address
        msg['Subject']=message_subject
        msg.attach(MIMEText(message_text,'plain'))
        msg['To']=','.join(to_list)
        text=msg.as_string()
        server=smtplib.SMTP('ucdavis-edu.mail.protection.outlook.com', 25)
        server.starttls()
        server.sendmail(email_address, to_list, text)
        server.quit()
    # The to_list should be cleansed of any ucdavis.edu clients at this point
    server=smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_address,email_password)
    msg = MIMEMultipart()
    msg['From']=email_address
    msg['Subject']=message_subject
    msg.attach(MIMEText(message_text,'plain'))
    msg['To']=','.join(outside_list)
    text=msg.as_string()
    server.sendmail(email_address, outside_list, text)
    server.quit()
    return 

def ReadEndOfFile(filename, n):
    """
    Retrieves the last n lines of a file.

    Args:
    - filename (str): The name of the file to read the end of.
    - n (int): The number of lines to retrieve.

    Returns:
    - Returns the last n columns as numpy arrays of strings.
    """
    proc=subprocess.Popen(['tail','-n',str(n),filename], stdout=subprocess.PIPE)
    soutput,sinput=proc.communicate()
    lines = soutput.decode().split('\n')
    lines.pop() # Strip last line, which is empty
    
    output=numpy.transpose([line.split() for line in lines])
    
    return output

def log_in(driver,website,login_email,login_password):
    # Navigate to the Ford vehicle-dashboard
    driver.get(website)
    time.sleep(17.9)

    # Find the username and password input fields and fill them in
    username_input = driver.find_element(By.ID,"signInName")  # Replace 'username' with the actual ID of the username input field
    password_input = driver.find_element(By.ID,"password")  # Replace 'password' with the actual ID of the password input field

    username_input.send_keys(login_email)
    password_input.send_keys(login_password)

    # Submit the form (assuming there's a login button to click)
    login_button = driver.find_element(By.ID,"next")  # Replace 'login-button' with the actual ID of the login button
    login_button.click()
    return
    
def read_odometer(driver):
    try:
        #scrape odometer value
        odometer = driver.find_element(By.CLASS_NAME,"number.current-mileage")
        odometer = odometer.text.split(" MI")[0].split(",")
        o=""
        for i in odometer:
            o=o+i
        odometer=int(o)
        return odometer
    except Exception as e:
        print(e)
        return False

def check_if_odometer_has_changed(odometerfile,odometervalue):
    try:
        currentdate,lastvalue = ReadEndOfFile(odometerfile, 1)
        lastvalue=int(lastvalue)
        if odometervalue == lastvalue:
            return False
    except Exception as e:
        print(e)
    return True

def read_miles_to_empty(driver):
    try:
        #scrape miles to empty
        miles_to_empty = driver.find_element(By.CLASS_NAME,"number.fuel-level")
        miles_to_empty = int(miles_to_empty.text.split(" MI")[0])
        return miles_to_empty
    except Exception as e:
        print(e)
        return False

def read_fuel_level(driver):
    try:
        #scrape fuel level from image
        fuel_level = driver.find_element(By.CLASS_NAME,"icon.fuel-level")
        fuel_level = fuel_level.get_attribute("src")
        fuel_level = fuel_level.split("/")[-1].split(".")[0].split("_")[-1]
        if fuel_level == "threefourth":
            fuel_level = 0.75
        elif fuel_level == "half":
            fuel_level = 0.5
        return fuel_level
    except Exception as e:
        print(e)
        return False

def read_oil_life(driver):
    try:
        #scrape oil life
        oil_life = driver.find_element(By.CLASS_NAME,"number.oil-life")
        oil_life = float(oil_life.text.split("%")[0])/100
        return oil_life
    except Exception as e:
        print(e)
        return False

def read_tire_pressure(driver):
    try:
        #scrape tire pressure
        tire_pressure = driver.find_elements(By.CLASS_NAME,"flex-item")
        left_tire_pressure=tire_pressure[0].text
        left_front_tire_pressure,left_back_tire_pressure=left_tire_pressure.split("\n")
        right_tire_pressure=tire_pressure[1].text
        right_front_tire_pressure,right_back_tire_pressure=right_tire_pressure.split("\n")
        left_front_tire_pressure,right_front_tire_pressure,left_back_tire_pressure,right_back_tire_pressure = int(left_front_tire_pressure),int(right_front_tire_pressure),int(left_back_tire_pressure),int(right_back_tire_pressure)
        return left_front_tire_pressure,right_front_tire_pressure,left_back_tire_pressure,right_back_tire_pressure
    except Exception as e:
        print(e)
        return False

def access_website(website,login_email,login_password,odometerfile,headless=True):
    # Start a new Chrome browser instance
    timeout=20
    
    if headless:
        # Set Chrome options to run in headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # Enable headless mode
    
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
    else:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.set_page_load_timeout(timeout)
    
    log_in(driver,website,login_email,login_password)
    
    attempt=0
    while attempt<3:
        try:
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CLASS_NAME,"number.current-mileage")))
            attempt+=4
        except TimeoutException:
            attempt+=1
            print("Page load timed out "+str(attempt)+" times.")
            driver.quit()
            time.sleep(5)
            log_in(driver,website,login_email,login_password)
             
    check=False
    odometer = read_odometer(driver)
    if odometer:
        check=check_if_odometer_has_changed(odometerfile,odometer)
    if check:
        miles_to_empty=read_miles_to_empty(driver)
        fuel_level=read_fuel_level(driver)
        oil_life=read_oil_life(driver)
        tire_pressure=read_tire_pressure(driver)
        #close the webdriver
        driver.quit()
        return odometer,miles_to_empty,fuel_level,oil_life,tire_pressure
    #close the webdriver
    driver.quit()
    return False

def write_data_file(date,odometer,miles_to_empty,fuel_level,oil_life,tire_pressure,odometerfile,fuelfile,oilfile,pressurefile):
    odfile = open(odometerfile, 'a')
    odfile.write(date+" "+str(odometer)+"\n")
    odfile.close()
    
    ffile = open(fuelfile, 'a')
    ffile.write(date+" "+str(miles_to_empty)+" "+str(fuel_level)+"\n")
    ffile.close()
    
    ofile = open(oilfile, 'a')
    ofile.write(date+" "+str(oil_life)+"\n")
    ofile.close()
    
    pfile = open(pressurefile, 'a')
    pfile.write(date+" "+str(tire_pressure[0])+" "+str(tire_pressure[1])+" "+str(tire_pressure[2])+" "+str(tire_pressure[3])+"\n")
    pfile.close()
    return

def update_years_list(year,yearfile):
    lastyear=ReadEndOfFile(yearfile, 1)
    if year!=lastyear:
        file = open(yearfile, 'a')
        file.write(year+"\n")
        file.close()
        return True
    return False

def scrape_data(date,yearfile,website,login_email,login_password,odometerfile,fuelfile,oilfile,pressurefile,headless=True):
    access=access_website(website,login_email,login_password,odometerfile,headless=headless)
    if access:
        odometer,miles_to_empty,fuel_level,oil_life,tire_pressure = access
        writing=write_data_file(date,odometer,miles_to_empty,fuel_level,oil_life,tire_pressure,odometerfile,fuelfile,oilfile,pressurefile)
        yearupdate=update_years_list(date[:4],yearfile)
        return True
    return False

def read_data(odometerfile,fuelfile,oilfile,pressurefile):
    odometer_dates,odometer_data=numpy.loadtxt(odometerfile,unpack=True)
    odometer_dates=numpy.array([datetime.datetime.strptime(str(int(single_date)),'%Y%m%d%H%M') for single_date in odometer_dates])
    
    fuel_dates,miles_data,fuel_data=numpy.loadtxt(fuelfile,unpack=True)
    fuel_dates=numpy.array([datetime.datetime.strptime(str(int(single_date)),'%Y%m%d%H%M') for single_date in fuel_dates])
    
    oil_dates,oil_data=numpy.loadtxt(oilfile,unpack=True)
    oil_dates=numpy.array([datetime.datetime.strptime(str(int(single_date)),'%Y%m%d%H%M') for single_date in oil_dates])

    pressure_dates,FL_pressure,FR_pressure,BL_pressure,BR_pressure=numpy.loadtxt(pressurefile,unpack=True)
    pressure_dates=numpy.array([datetime.datetime.strptime(str(int(single_date)),'%Y%m%d%H%M') for single_date in pressure_dates])
    return odometer_dates,odometer_data,fuel_dates,miles_data,fuel_data,oil_dates,oil_data,pressure_dates,FL_pressure,FR_pressure,BL_pressure,BR_pressure

def read_years(yearfile):
    years=[numpy.loadtxt(yearfile,unpack=True)]
    years=[str(int(year)) for year in years]
    return years

def make_plots(yearfile,maindir,save=False,savefile=None):
    years=read_years(yearfile)
    
    fig = plt.figure(1, figsize=(10,6))
    fig.patch.set_facecolor('white')
    
    ax1=fig.add_subplot(2,2,1)
    ax1.set_ylabel("Odometer (Miles Since Start of Year)")
    ax1.set_xlabel("Date (Days Since First use of Year)")
    
    ax2=fig.add_subplot(2,2,2)
    ax2.set_ylabel("Miles to Empty")
    ax2.set_xlabel("Date (Days Since First use of Year)")
    
    ax3=fig.add_subplot(2,2,3)
    ax3.set_ylabel("Oil Life (%)")
    ax3.set_xlabel("Date (Days Since First use of Year)")
    
    ax4=fig.add_subplot(2,2,4)
    ax4.set_ylabel("Tire Pressure")
    ax4.set_xlabel("Date (Days Since First use of Year)")
    
    #plot max miles to empty over time
    #plot miles per gallon
    
    for year in years:
        odometerfile=maindir+year+"odometer.dat"
        fuelfile=maindir+year+"fuel.dat"
        oilfile=maindir+year+"oil.dat"
        pressurefile=maindir+year+"pressure.dat"
        odometer_dates,odometer_data,fuel_dates,miles_data,fuel_data,oil_dates,oil_data,pressure_dates,FL_pressure,FR_pressure,BL_pressure,BR_pressure=read_data(odometerfile,fuelfile,oilfile,pressurefile)
        odometer_dates=odometer_dates-odometer_dates[0]
        odometer_dates=[(thisdate.seconds)/86400 for thisdate in odometer_dates]
        ax1.plot(odometer_dates,odometer_data-odometer_data[0],'o-',label=year)
        ax2.plot(odometer_dates,miles_data,'o-',label=year)
        #ax2.plot(odometer_dates,fuel_data,'o-',label=year) update once we have good data
        ax3.plot(odometer_dates,oil_data,'o-',label=year)
        ax4.plot(odometer_dates,FL_pressure,'o-',label="FL "+year)
        ax4.plot(odometer_dates,FR_pressure,'o-',label="FR "+year)
        ax4.plot(odometer_dates,BL_pressure,'o-',label="BL "+year)
        ax4.plot(odometer_dates,BR_pressure,'o-',label="BR "+year)
        if year==years[-1]:
            ax1.set_title("Odometer Mileage. "+str(odometer_data[-1])+" Miles Total.")
            a2title="Miles to Empty Over Time. Currently "+str(miles_data[-1])+" Miles."
            ax2.set_title(a2title)
            ax3.set_title("Oil Lifetime Remaining. Currently "+str(oil_data)+"%")
            ax4.set_title("Tire Pressure.")
            
        plt.tight_layout()
    ax1.legend(loc='upper left')
    ax2.legend(loc='lower left')
    ax3.legend(loc='lower left')
    ax4.legend(loc='lower left')
    if save:
        plt.savefig(maindir+savefile)
    return
