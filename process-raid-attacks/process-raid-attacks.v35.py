#!/usr/bin/python
import sys
import csv

if len(sys.argv) < 4:
	print "Check the given parameters." 
	print "Expecting:"
	print " min-attacks (12)"
	print " kick-at (3)"
	print " list of CSV files (without header)"
	sys.exit (0)

MIN_ATTACKS = int (sys.argv[1]) # Our default is 12
KICK_AT     = int (sys.argv[2]) # Our default is 3
WARN_AT     = KICK_AT - 1

if MIN_ATTACKS <= 0:
	print "Hey! min-attacks should be a positive value!"
	sys.exit (0)

if KICK_AT <= 0:
	print "Hey! kick-at should be a positive value!"
	sys.exit (0)

CNT_min_attacks = {} # dictionary [userid->#attacks] that have not surpassed MIN_ATTACKS at least 1
CNT_names = {}       # dictionary [userid->list(nicks)]

for f in range(3, len(sys.argv)):
	with open(sys.argv[f], 'rb') as f:
		reader = csv.reader(f)
		next(reader, None) # Skip the header
		for row in reader:
			userid = row[1]
			if row[0] in CNT_names:
				CNT_names[ userid ].append (row[0])
			else:
				CNT_names[ userid ] = list() 
				CNT_names[ userid ].append (row[0])
		f.close()

for f in range(3, len(sys.argv)):
	with open(sys.argv[f], 'rb') as f:
		reader = csv.reader(f)
		next(reader, None) # Skip the header
		prevuser = None
		for row in reader:
			# Store user IDs (not names) that have not attacked at least MIN_ATTACKS
			# Also store names seen for this user ID (in case user has changed its nick)
			if prevuser != row[1]:
				prevuser = row[1]
				if int(row[2]) < MIN_ATTACKS:
					userid = row[1]
					if userid in CNT_min_attacks:
						CNT_min_attacks[ userid ] = CNT_min_attacks[ userid ] + 1
					else:
						CNT_min_attacks[ userid ] = 1
		f.close()

# Double 0 attack analysis
CNT_0_attacks = {} # dictionary [userid->#attacks] that have not surpassed MIN_ATTACKS at least 1
KICK_0 = list() # list of userids that have not attacked at least twice (2) AT ALL in the last two raids

if len(sys.argv) > 4:
	for f in range(len(sys.argv)-2, len(sys.argv)):
		with open(sys.argv[f], 'rb') as f:
			reader = csv.reader(f)
			next(reader, None) # Skip the header
			prevuser = None
			for row in reader:
				# Store user IDs (not names) that have not attacked at least MIN_ATTACKS
				# Also store names seen for this user ID (in case user has changed its nick)
				if prevuser != row[1]:
					prevuser = row[1]
					if int(row[2]) == 0:
						userid = row[1]
						if userid in CNT_0_attacks:
							CNT_0_attacks[ userid ] = CNT_0_attacks[ userid ] + 1
							if CNT_0_attacks[ userid ] == 2:
								KICK_0.append (userid)
						else:
							CNT_0_attacks[ userid ] = 1
			f.close()

WARN_0 = list() # list of userids that have not attacked AT ALL in last raid

with open(sys.argv[len(sys.argv)-1], 'rb') as f:
	reader = csv.reader(f)
	next(reader, None) # Skip the header
	prevuser = None
	for row in reader:
		# Store user IDs (not names) that have not attacked at least MIN_ATTACKS
		# Also store names seen for this user ID (in case user has changed its nick)
		if prevuser != row[1]:
			prevuser = row[1]
			if int(row[2]) == 0:
				userid = row[1]
				# If user was not already in kick list, and not already in warn list, add it
				if userid not in WARN_0 and userid not in KICK_0:
					WARN_0.append (userid)
	f.close()

KICK = list() # list of userids that have not attacked at least KICK_AT
WARN = list() # list of userids that deserve a warning
for userid, v in CNT_min_attacks.iteritems():
	if v == KICK_AT and userid not in KICK_0:
		KICK.append (userid)
	if v == WARN_AT and userid not in KICK_0 and userid not in WARN_0:
		WARN.append (userid)

print ""
if len(KICK_0) > 0:
	print "Users to be kicked because double 0 attack."
	print "---"
	for userid in KICK_0:
		print "User: "+ str(userid) +" - Nick:"+ ",".join (CNT_names[userid])
	print ""

if len(WARN_0) > 0:
	print "Users to be warned because last 0 attack."
	print "---"
	for userid in WARN_0:
		print "User: "+ str(userid) +" - Nick:"+ ",".join (CNT_names[userid])
	print ""

if len(KICK) > 0:
	print "Users to be kicked because failed to attack "+str(MIN_ATTACKS)+" times in "+str(KICK_AT)+" raids:"
	print "---"
	for userid in KICK:
		print "User: " + str(userid) +" - Nick: "+ ", ".join (CNT_names[userid])
	print ""

if len(WARN) > 0:
	print "Users to be warned because failed to attack "+str(MIN_ATTACKS)+" times in "+str(WARN_AT)+" raids:"
	print "---"
	for userid in WARN:
		print "User: " + str(userid) +" - Nick: "+ ", ".join (CNT_names[userid])
	print ""


#
# Check for inappropriate armor attacks. e.g. attacking STERL's arms/hands or MOHACA's torso is inappropiate because the
# armor is so high or the titan lord can be killed by focusing other parts and thus save time/energy.
# We don't check for non-armor attacks, if they have been exposed it is ok to take advantage of them
# Use a threshold of 0.20 to allow some mis-taps into the offending areas
#
# Process only the LAST REPORT

#PlayerName,PlayerCode,TotalRaidAttacks,TitanNumber,TitanName,TitanDamage,ArmorHead,ArmorTorso,ArmorLeftArm,ArmorRightArm,ArmorLeftHand,ArmorRightHand,ArmorLeftLeg,ArmorRightLeg,BodyHead,BodyTorso,BodyLeftArm,BodyRightArm,BodyLeftHand,BodyRightHand,BodyLeftLeg,BodyRightLeg,SkeletonHead,SkeletonTorso,SkeletonLeftArm,SkeletonRightArm,SkeletonLeftHand,SkeletonRightHand,SkeletonLeftLeg,SkeletonRightLeg

STERL = list() # list of userids that have attacked STERL's inappropriate armor
MOHACA = list() # list of userids that have attacked MOHACA's inappropriate armor
JUKK = list() # list of userids that have attacked MOHACA's inappropriate armor
with open(sys.argv[len(sys.argv)-1], 'rb') as f:
	reader = csv.reader(f)
	next(reader, None) # Skip the header
	for row in reader:
		Total = int(row[5])
		TitanName = str(row[4])
		if TitanName.startswith('Sterl') and Total > 0:
			Arms  = int(row[8])+int(row[9]) 
			Hands = int(row[10])+int(row[11])
			if float (Arms+Hands) / float (Total) > 0.20:
				if row[1] not in STERL:
					STERL.append (row[1])
		elif TitanName.startswith('Mohaca') and Total > 0:
			Torso = int(row[7]) 
			if float (Torso) / float (Total) > 0.20:
				if row[1] not in MOHACA:
					MOHACA.append (row[1])
		elif TitanName.startswith('Jukk') and Total > 0:
			Arms  = int(row[8])+int(row[9]) 
			Hands = int(row[10])+int(row[11])
			if float (Arms+Hands) / float (Total) > 0.20:
				if row[1] not in MOHACA:
					JUKK.append (row[1])
	f.close()

if len(STERL) > 0:
	print "Users that attacked STERL's arms/hands armor:"
	print "--"
	for userid in STERL:
		print "User: " + userid +" - Nick: "+ ", ".join(CNT_names[userid])
	print ""
if len(MOHACA) > 0:
	print "Users that attacked MOHACA's torso armor:"
	print "--"
	for userid in MOHACA:
		print "User: " + str(userid) +" - Nick: "+ ", ".join (CNT_names[userid])
	print ""
if len(JUKK) > 0:
	print "Users that attacked JUKK's arms/hands armor:"
	print "--"
	for userid in JUKK:
		print "User: " + str(userid) +" - Nick: "+ ", ".join (CNT_names[userid])
	print ""
