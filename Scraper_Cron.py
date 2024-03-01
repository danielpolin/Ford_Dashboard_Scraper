import FordDashboardScraper,time

login_email="[YOUR_EMAIL]"
login_password="[YOUR_FORD_PASSWORD]"
website="https://www.ford.com/support/vehicle-dashboard/"

send_addr="[EMAIL_TO_SEND_FROM]"
adresses=['[EMAIL_TO_SEND_TO]']
send_addr_password='[SEND_EMAIL_PASSWORD]'

date = time.strftime('%Y%m%d%H%M')
year = date[:4]

maindir="[Your_Directory]"
odometerfile=maindir+"Log_Files/"+year+"odometer.dat"
fuelfile=maindir+"Log_Files/"+year+"fuel.dat"
oilfile=maindir+"Log_Files/"+year+"oil.dat"
pressurefile=maindir+"Log_Files/"+year+"pressure.dat"
yearfile=maindir+"Log_Files/"+"years.dat"

savefile="Log_Files/DashboardPlots.png"

scrapersuccess=FordDashboardScraper.scrape_data(date,yearfile,website,login_email,login_password,odometerfile,fuelfile,oilfile,pressurefile,headless=True)
if scrapersuccess:
    FordDashboardScraper.make_plots(yearfile,maindir,save=True,savefile=savefile)
