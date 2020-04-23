During the Dockerfile configuration process, there are numerous variables that are used:

Namely, Environmental variable (in the container & build), Argument to the Dockerfile (provided usually by the DockerCompose)

In this case: 

Variables such as

ARG ARGS_MySQLUser=DefaultMySQLUser
ENV MySQLUser ${ARGS_MySQLUser} 
