#!/usr/bin/env python
"""
Program to start notebooks

Usage:

example:
autoAnalysis/start_nbs.py sql $HOSTNAME $PWD/users users.csv
"""
import sys
import json
import csv
import random
import os
import subprocess
import socket
import string

def rm_docker(containerId):
  cmd = ['docker', 'stop', containerId]
  subprocess.call(cmd)
  cmd = ['docker', 'rm', containerId]
  subprocess.call(cmd)

def main():
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("--server",   default=socket.gethostname(), help="server name")
  parser.add_argument("--csv_fn",   default='users.csv')
  parser.add_argument("--registry", default=None)
  parser.add_argument('action',     help="stop, start, restart")
  parser.add_argument("docker_tag", help="The tag of the docker image to use - also used as a prefix")
  parser.add_argument("docker_run", help="Filename containing a template for the docker run command")
  
  args = parser.parse_args()
  
  docker_tag = args.docker_tag
  docker_run = args.docker_run
  csv_fn = os.path.abspath(args.csv_fn)
  BASE = os.path.dirname(csv_fn)
  server = args.server
  if args.action not in ['start', 'stop', 'restart']:
    print "Invalid action", args.action
    sys.exit(1)
  
  with open(docker_run) as f:
    docker_run_template = string.Template(f.read())
  
  # read all users
  with open(csv_fn) as csvfile:
    reader = csv.DictReader(csvfile, delimiter='\t')
    students = [ row for row in reader ]

  # get running containers
  proc = subprocess.Popen(['docker','ps', '-a'],stdout=subprocess.PIPE)
  next(proc.stdout) # ignore first line
  runningContainers = [ line.strip().split()[-1] for line in proc.stdout ] 
    
  if args.action == 'stop':
    for containerId in runningContainers:
      print containerId
      if containerId.endswith('_' + args.docker_tag):
        rm_docker(containerId)
    sys.exit(0)
  
  # create exchange directory
  exchange_dn = os.path.join(BASE, 'exchange')
  if not os.path.isdir(exchange_dn):
    os.mkdir(exchange_dn)      

  id_field = 'SNumber'
  admin_field = 'Admin'
  password_field = 'Password'
  server_field = 'server'
  port_field = 'port'
  
  # determine docker image name
  docker_image = docker_tag
  if args.registry:
    docker_image = args.registry + '/' + docker_image

  # iterate through students and create those that should be running on this server
  for student in students:
    id = student[id_field]
    containerId = id + "_" + docker_tag
    
    
    if containerId in runningContainers and args.action == 'restart': 
      print "Stoping existing", containerId
      rm_docker(containerId)
    if containerId in runningContainers and args.action == 'start': 
      continue
    
    #print containerId, student[server_field], server
        
    # if the container for this user shouldn't be run on this server...
    if student[server_field] != server and server != '*': continue
    
    print 'Starting', containerId
    
    # Determine home directory
    if student[admin_field] != "TRUE":
      home_dn = os.path.join(BASE, 'students', id)
    else:
      home_dn = BASE
    if not os.path.isdir(home_dn):
      os.makedirs(home_dn)
    
    student['USERID'] = os.getuid();
    student['HOME'] = home_dn;
    student['EXCHANGE'] = exchange_dn;
    student['CONTAINERID'] = containerId
    student['DOCKERIMAGE'] = docker_image
    
    cmd = docker_run_template.safe_substitute(student).replace('\n', ' ')
    print cmd
    subprocess.call(cmd, shell=True)
      
if __name__ == '__main__':
  main()
