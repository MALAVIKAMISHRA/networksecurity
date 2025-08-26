from setuptools import find_packages,setup
from typing import List


###This file is responsible for packaging and distributing python projects.it is used by setuptools to define configuration of project,such as metadata,dependencies and more.###

def get_requirements()->List[str]:
    """This function will return list of requirements"""
    requirement_lst:List[str]=[]
    try:
        with open('requirements.txt') as file:
            lines=file.readlines()
            #process each line
            for line in lines:
                ##to remove space
                requirement=line.strip()
                ##ignore '-e.'
                if requirement and requirement!='-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirements.txt file not found")

    return requirement_lst  

setup(
    name="NetworkSecurity",
    version="0.0.1",
    author="Malavika Mishra",
    author_email="malavikamishra89@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements()
)  