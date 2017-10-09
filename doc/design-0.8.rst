
RestAPI (``api`` app) 
---------------------

A RESTful API will be developed, using Django Rest Framework to expose models from
``hwdoc`` app.

API will expose the following models:

+--------------------+-------------------------+-------------------------+
|      Model         |        Endpoint         | GET parameter filtering |
+====================+=========================+=========================+
|``Equipment``       |``/api/equipment``       |      ``?serial=``       |
+--------------------+-------------------------+-------------------------+
|``Rack``            |``/api/rack``            |      ``?name=``         |
+--------------------+-------------------------+-------------------------+
|``Project``         |``/api/project``         |     ``(None)``          |
+--------------------+-------------------------+-------------------------+
|``ServerManagement``|``/api/servermanagement``|      ``?name=``         |
+--------------------+-------------------------+-------------------------+

Top level urls (e.g. ``/api/rack`` ) return a list with all the objects of the equivalent model

An example query and result is presented below

``/api/equipment/?serial='KDWDKKA'``
::


 [  
    {
        "serial": "KDWDKKA", 
        "ipmi": {
            "IPMI Mac": null, 
            "IPMI Hostname": null
        }, 
        "model": {
            "name": "System x3550", 
            "vendor": "IBM"
        }, 
        "datacenter": "KOLETTI", 
        "rack": {
            "rackunit": 41, 
            "rack": "KAR08"
        }, 
        "unit": 41, 
        "orientation": "Front", 
        "project": "EETT measurementlab (MLAB)", 
        "purpose": "", 
        "comments": "", 
        "keyvalue_attrs": {}
    }
 ]