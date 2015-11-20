# How to unpack Initial Data:

Initial Data are stored in `JSON` format, and are compliant with 
the specifications of Django `loaddata` models.

To **unpack** the archive (`.tar.bz2`), it is simply required
to execute the following command:

    tar -xvjf initial_data.json.tar.bz2 initial_data.json
    
To **re-create** the compressed archive in the same `tar.bz2` format, the 
following command is required:

    tar -cvjf initial_data.json.tar.bz2 initial_data.json
    
    
