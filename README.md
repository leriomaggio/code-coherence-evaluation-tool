# Code Coherence Evaluation Tool
Django-Admin based web application supporting automatic code analysis, 
code reading, and code-comments coherence evaluation.

The application has been developed to support the creation of the 
[**Coherence Dataset**](http://www2.unibas.it/gscanniello/coherence/), 
a publicly available benchmark containing annotated `(code, comments)`
pairs, and their corresponding Coherence evaluation.

# Main Dependencies

The whole code base of the project has been developed in **Python 3**, and in **Django 1.6.x**.

Other dependencies are:

* `celery` and `rabbitmq`: necessary in the code analysis phase, which is activated every time a 
    new project is uploaded;
* `Antlr3` (included): to support Java Code Analysis 
    (**Note**: So far, only the analysis of Java code is supported)

# Setup

To setup the entire project, it is required to have a Python environment properly configured 
as to satisfy all the package dependencies. 

For the sake of simplicity, these dependencies have been collected in the `requirements.txt` file by
the `pip freeze` command.
<br />
Thus, to install all the dependencies, it is just required to execute the following command:

    pip install -r requirements.txt
    
To avoid polluting the main system (Python) environment, it is highly suggested to create a
proper *virtual environment* for the specific sake:

    venv -p python3 <DEST_DIR>
    source <DEST_DIR>/bin/activate
    pip install -r requirements.txt
    
## Setup Database
    Once the environment has been properly set up, it is finally necessary to create a database 
    using **PostgreSQL** (`9.3`). For further details on this, please refer to the 
    [official documentation](http://www.postgresql.org/docs/9.3/static/), 
    depending on your machine and operating system.
    
    Please refer to the `DATABASES` directive in the *Main Settings* 
    (`code_comments_coherence/code_comments_coherence/settings.py`) to see the details about 
    database name and corresponding authentication parameters.

## Restore Database

    The code ships with the set of initial data to **re-create** the database from scratch.
    
    The data are provided in the form of `fixtures`, located in the `source_code_analysis/fixture` folder.
    
    This folder contains the `initial_data` archive, and the corresponding instructions to unpack it.
     
    To recreate the entire (*Structure+Data*), it is necessary to execute the following command:
    
        python manage.py syncdb

# References

A. Corazza, V. Maggio, G. Scanniello, *On the Coherence Between Comments and Implementations in Source Code*,
In Procs of **41st EUROMICRO Conference on Software Engineering and Advanced Applications** (SEAA), 
*26-28 Aug. 2015*, Madeira (Portugal) **DOI**: `10.1109/SEAA.2015.20` 
