# SimpleHistoryExample.py
from __future__ import print_function
from __future__ import absolute_import
import blpapi
from optparse import OptionParser


class BloombergAPI:
    
    def __init__(self,SERVER_HOST='localhost',SERVER_PORT=8194):
        
        # Fill SessionOptions
        sessionOptions = blpapi.SessionOptions()
        sessionOptions.setServerHost("localhost")
        sessionOptions.setServerPort(8194)
            
        # Create a Session
        self.session = blpapi.Session(sessionOptions)    
        
        self.session_started = self.session.start()
        
        # Start a Session
        if not self.session_started:
            print("Failed to start session.")
            #return
        
        self.service_open = self.session.openService("//blp/refdata")
        
       
        # Open service to get historical data from
        if not self.service_open:
            print("Failed to open //blp/refdata")

  
    def send_request(self,securities,fields,startdate,enddate):
        #options = parseCmdLine()
    
        # Fill SessionOptions
        #sessionOptions = blpapi.SessionOptions()
        #sessionOptions.setServerHost("localhost")
        #sessionOptions.setServerPort(8194)
    
        #print("Connecting to %s:%s" % (options.host, options.port))
        # Create a Session
        #session = blpapi.Session(sessionOptions)
    
        # Start a Session
        #if not session.start():
        #    print("Failed to start session.")
            #return
    
        #try:
            # Open service to get historical data from
        #    if not session.openService("//blp/refdata"):
        #        print("Failed to open //blp/refdata")
                #return
        if self.service_open:
            
            # Obtain previously opened service
            refDataService = self.session.getService("//blp/refdata")
    
            # Create and fill the request for the historical data
            request = refDataService.createRequest("HistoricalDataRequest")
            
            for security in securities:
                request.getElement("securities").appendValue(security)
            #request.getElement("securities").appendValue("MSFT US Equity")
            
            
            fields = fields# + ["date"]
            
            for field in fields:
                request.getElement("fields").appendValue(field)
            #request.getElement("fields").appendValue("OPEN")
            request.set("periodicityAdjustment", "ACTUAL")
            
            request.set("periodicitySelection", "DAILY")
            
      
            request.set("startDate", startdate.strftime("%Y%m%d"))
            request.set("endDate", enddate.strftime("%Y%m%d"))
            
    
            self.session.sendRequest(request)
    
            response = {}
    
            while(True):
    
                ev = self.session.nextEvent(500)
    
                for msg in ev:
                  
                    if(msg.hasElement("securityData")):
                        
                        sec_data = msg.getElement("securityData")
                        security = sec_data.getElement("security").getValueAsString()
                        
                        
                        entries = {}
                        if(sec_data.hasElement("fieldData")):
                            
                            field_data = sec_data.getElement("fieldData")
                            
                            for i in range(0,field_data.numValues()):
                                
                                element    = field_data.getValueAsElement(i)
                                time_stamp = element.getElement(0).getValueAsDatetime()
                                
                                field_entries = {}
                                for f in fields:
                                    field_entries.update({f:element.getElementValue(f)})
                                entries.update({time_stamp:field_entries})
                        response.update({security:entries})
     
                if ev.eventType() == blpapi.Event.RESPONSE:
                    # Response completly received, so we could exit
                    break
            return response
        
        else:
            print('ERROR: Service is not open!')
            # Stop the session
            
            

#%%

if __name__ == "__main__":
    
    from datetime import datetime
    import pandas
    
    try:
        data = send_request(["MSFT US Equity","IBM US Equity"],["PX_LAST"],datetime(2000,1,1),datetime(2010,1,1))
    except KeyboardInterrupt:
        print("Ctrl+C pressed. Stopping...")
    
    frames = []
    for k,v in data.items():
        f = pandas.DataFrame.from_dict(v,orient='index')
        
        f.columns = [k]
        frames.append(f)
        
    df = pandas.concat(frames,axis=1)