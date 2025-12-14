-- =====================================================
-- Operation Bella Ciao - Data Population Script (CORRECTED)
-- Team: DnA_Not_Found (Team 54)
-- =====================================================

USE bellaciao_db;

-- Table: HEIST_BLUEPRINT
INSERT INTO HEIST_BLUEPRINT (BlueprintID, LocationName, ArchitectBlindspot) VALUES
(1, 'Royal Mint of Spain', 'North ventilation shaft'),
(2, 'Bank of Spain', 'Underground tunnel entrance'),
(3, 'Gold Reserve Vault', 'East side security blind spot');

-- Table: KEYRMS (Must come after HEIST_BLUEPRINT)
INSERT INTO KEYRMS (BlueprintID, Keyrooms) VALUES
(1, 'Printing Room'),
(1, 'Control Room'),
(1, 'Roof Access Point'),
(2, 'Gold Vault'),
(2, 'Governor''s Office'),
(3, 'East Security Post');

-- Table: CREW_MEMBER (FIXED: Lastname -> LastName, Specialisation -> Specialization, Loyalty_Score -> LoyaltyScore)
INSERT INTO CREW_MEMBER (CodeName, HeistID, FirstName, LastName, Specialization, LoyaltyScore) VALUES
('Professor', 1, 'Sergio', 'Marquina', 'Mastermind', 100),
('Berlin', 1, 'Andres', 'de Fonollosa', 'Field Commander', 95),
('Tokyo', 1, 'Silene', 'Oliveira', 'Assault Specialist', 75),
('Rio', 1, 'Anibal', 'Cortes', 'Hacker', 80),
('Nairobi', 1, 'Agata', 'Jimenez', 'Quality Control', 90),
('Denver', 1, 'Daniel', 'Ramos', 'Security Expert', 85),
('Helsinki', 1, 'Mirko', 'Dragic', 'Combat Specialist', 88),
('Oslo', 1, 'Radko', 'Dragic', 'Heavy Support', 87),
('Moscow', 1, 'Agustin', 'Ramos', 'Excavation Expert', 92),
('Stockholm', 2, 'Monica', 'Gaztambide', 'Inside Contact', 70),
('Lisbon', 2, 'Raquel', 'Murillo', 'Negotiator', 95),
('Palermo', 2, 'Martin', 'Berrote', 'Engineer', 78),
('Marseille', 3, 'Javier', 'unknown', 'Infiltration', 82),
('Bogota', 3, 'Santiago', 'unknown', 'Welding Expert', 79);

-- Table: TRAITS (multivalued attribute)
INSERT INTO TRAITS (Crew_No, VolatileTraits) VALUES
('Tokyo', 'Impulsive'),
('Tokyo', 'Hot-tempered'),
('Berlin', 'Narcissistic'),
('Berlin', 'Unpredictable'),
('Denver', 'Nervous laughter'),
('Oslo', 'Aggressive tendencies'),
('Palermo', 'Obsessive'),
('Stockholm', 'Stockholm syndrome');

-- Table: STRATEGIC_CREW
INSERT INTO STRATEGIC_CREW (Codename, SecurityClearanceLevel) VALUES
('Professor', 'Level 10'),
('Berlin', 'Level 9'),
('Lisbon', 'Level 8'),
('Palermo', 'Level 7');

-- Table: TACTICAL_CREW
INSERT INTO TACTICAL_CREW (Codename, WeaponProficiency) VALUES
('Tokyo', 'Expert Marksman'),
('Helsinki', 'Heavy Weapons'),
('Oslo', 'Close Combat'),
('Denver', 'Tactical Defense');

-- Table: TECHNICAL_CREW
INSERT INTO TECHNICAL_CREW (Codename, TechnicalCertification) VALUES
('Rio', 'Certified Ethical Hacker'),
('Nairobi', 'Counterfeit Specialist'),
('Moscow', 'Mining Engineer'),
('Bogota', 'Welding Certification'),
('Marseille', 'Forensics Expert');

-- Table: RESOURCE (FIXED: Current_Quantity -> CurrentQuantity)
INSERT INTO RESOURCE (ResourceID, Type, CurrentQuantity, CriticalThreshold) VALUES
(1, 'Assault Rifles', 50, 10),
(2, 'Ammunition', 5000, 500),
(3, 'Explosives', 200, 20),
(4, 'Zip Ties', 300, 50),
(5, 'Medical Supplies', 100, 15),
(6, 'Food Rations', 500, 100),
(7, 'Communication Devices', 30, 5),
(8, 'Drilling Equipment', 5, 1),
(9, 'Welding Tools', 10, 2),
(10, 'Computers', 15, 3);

-- Table: POLICE_UNIT
INSERT INTO POLICE_UNIT (UnitID, CommanderName, UnitType, PredictableCounter, Morale) VALUES
(1, 'Alicia Sierra', 'Special Operations', 85, 75),
(2, 'Angel Rubio', 'Tactical Response', 70, 80),
(3, 'Colonel Prieto', 'Command Unit', 90, 70),
(4, 'Suarez', 'Negotiation Team', 60, 85),
(5, 'Tamayo', 'Intelligence', 95, 65);

-- Table: PLAN_PHASE (FIXED: Phase_ID -> PhaseID)
INSERT INTO PLAN_PHASE (PhaseID, Phasecodename, Planned_Duration, Current_Dissonance) VALUES
(1, 'Entry', 2, 0),
(2, 'Hostage Capture', 3, 5),
(3, 'Printing Money', 120, 15),
(4, 'Tunnel Excavation', 48, 20),
(5, 'Gold Melting', 72, 10),
(6, 'Negotiation', 24, 25),
(7, 'Exit Strategy', 4, 30);

-- Table: HOSTAGE (FIXED: Blueprintid -> BlueprintID)
INSERT INTO HOSTAGE (HostageID, FirstName, LastName, Status, Usefulness, InstigatorFlag, ManagerCodename, BlueprintID) VALUES
(1, 'Arturo', 'Roman', 'Cooperative', 3, TRUE, 'Berlin', 1),
(2, 'Alison', 'Parker', 'Resistant', 8, FALSE, 'Nairobi', 1),
(3, 'Pablo', 'unknown', 'Neutral', 5, FALSE, 'Denver', 1),
(4, 'Mercedes', 'Colmenar', 'Cooperative', 7, FALSE, 'Moscow', 1),
(5, 'Cesar', 'Gandia', 'Hostile', 2, TRUE, 'Berlin', 2),
(6, 'Amanda', 'unknown', 'Cooperative', 6, FALSE, 'Helsinki', 2),
(7, 'Julia', 'unknown', 'Neutral', 4, FALSE, 'Lisbon', 2),
(8, 'Miguel', 'unknown', 'Resistant', 3, FALSE, 'Palermo', 2),
(9, 'Rafael', 'unknown', 'Cooperative', 5, FALSE, 'Stockholm', 1),
(10, 'Elena', 'unknown', 'Neutral', 6, FALSE, 'Nairobi', 1);

-- Table: PSYCHOLOGICAL_REPORT
INSERT INTO PSYCHOLOGICAL_REPORT (Crew_Member, ReportTimestamp, Frequency, MoralCompromiseLog) VALUES
('Tokyo', '2024-05-01 10:00:00', 'High', 'Impulsive behavior noted during hostage interaction'),
('Tokyo', '2024-05-01 22:00:00', 'Very High', 'Emotional outburst, threatened officer'),
('Berlin', '2024-05-01 16:00:00', 'Medium', 'Maintaining composure, slight arrogance'),
('Rio', '2024-05-02 04:00:00', 'Low', 'Anxiety due to police tracking'),
('Denver', '2024-05-02 10:00:00', 'Medium', 'Nervous laughter episodes increasing'),
('Stockholm', '2024-05-02 16:00:00', 'High', 'Empathy towards hostages developing'),
('Palermo', '2024-05-02 22:00:00', 'Very High', 'Obsessive behavior about plan details'),
('Nairobi', '2024-05-01 18:00:00', 'Low', 'Strong leadership, moral grounding');

-- Table: HOSTAGE_LOG (FIXED: HOSTAGE_ID -> HostageID)
INSERT INTO HOSTAGE_LOG (HostageID, Interaction_Timestamp, Interacting_Crew, Interaction_Type, Summary) VALUES
(1, '2024-05-01 11:00:00', 'Berlin', 'Interrogation', 'Demanded cooperation, threatened consequences'),
(1, '2024-05-01 15:00:00', 'Tokyo', 'Confrontation', 'Verbal altercation, hostage provoked crew'),
(2, '2024-05-01 12:00:00', 'Nairobi', 'Care', 'Provided medical attention, built trust'),
(3, '2024-05-01 13:00:00', 'Denver', 'Monitoring', 'Standard supervision, no incidents'),
(5, '2024-05-01 14:00:00', 'Berlin', 'Interrogation', 'Head of security, high-risk individual'),
(5, '2024-05-02 06:00:00', 'Helsinki', 'Confrontation', 'Physical altercation, hostage restrained'),
(6, '2024-05-01 16:00:00', 'Lisbon', 'Negotiation', 'Used as bargaining chip with police'),
(1, '2024-05-02 01:00:00', 'Professor', 'Psychological', 'Remote psychological manipulation');

-- Table: ASSIGNED_TO
INSERT INTO ASSIGNED_TO (Cname, Phase_id) VALUES
('Professor', 1),
('Professor', 3),
('Professor', 6),
('Professor', 7),
('Berlin', 1),
('Berlin', 2),
('Berlin', 6),
('Tokyo', 1),
('Tokyo', 2),
('Rio', 3),
('Rio', 7),
('Nairobi', 3),
('Denver', 2),
('Helsinki', 1),
('Helsinki', 2),
('Oslo', 1),
('Oslo', 2),
('Moscow', 4),
('Stockholm', 2),
('Stockholm', 6),
('Lisbon', 6),
('Palermo', 4),
('Palermo', 5),
('Marseille', 1),
('Bogota', 5);

-- Table: MONITORS
INSERT INTO MONITORS (Unit_id, Bprint_id) VALUES
(1, 1),
(1, 2),
(2, 1),
(3, 1),
(3, 2),
(4, 1),
(4, 2),
(5, 1),
(5, 2),
(5, 3);

-- Table: REQUIRES
INSERT INTO REQUIRES (Phase, Res_id) VALUES
(1, 1),
(1, 4),
(1, 7),
(2, 1),
(2, 4),
(2, 5),
(3, 6),
(3, 10),
(4, 8),
(4, 9),
(5, 3),
(5, 9),
(6, 7),
(7, 1),
(7, 2),
(7, 7);

-- Table: DEVIATES_FROM
INSERT INTO DEVIATES_FROM (C_id, P_id) VALUES
('Tokyo', 2),
('Tokyo', 6),
('Berlin', 3),
('Denver', 2),
('Palermo', 5),
('Stockholm', 2);

-- Table: COMMUNICATES_WITH
INSERT INTO COMMUNICATES_WITH (Codeid, Uid) VALUES
('Professor', 1),
('Professor', 4),
('Professor', 5),
('Lisbon', 1),
('Lisbon', 4),
('Berlin', 3),
('Berlin', 4);

-- Table: IS_LOCATED_IN
INSERT INTO IS_LOCATED_IN (h_id, BPid) VALUES
(1, 1),
(2, 1),
(3, 1),
(4, 1),
(9, 1),
(10, 1),
(5, 2),
(6, 2),
(7, 2),
(8, 2);

-- Table: NEGOTIATION
INSERT INTO NEGOTIATION (P_unit, crew_id, Hostageid, resource_id) VALUES
(4, 'Professor', 1, 6),
(4, 'Professor', 2, 5),
(1, 'Lisbon', 6, 7),
(4, 'Berlin', 5, 1),
(5, 'Professor', 1, 2);

-- Table: TASK_ASSIGNMENT (FIXED: Cname -> CName to match schema)
INSERT INTO TASK_ASSIGNMENT (PID, CName, ResID, BID) VALUES
(1, 'Berlin', 1, 1),
(1, 'Tokyo', 1, 1),
(1, 'Helsinki', 1, 1),
(2, 'Denver', 4, 1),
(2, 'Nairobi', 5, 1),
(3, 'Nairobi', 10, 1),
(3, 'Rio', 10, 1),
(4, 'Moscow', 8, 2),
(4, 'Palermo', 8, 2),
(5, 'Bogota', 9, 2),
(5, 'Palermo', 3, 2),
(6, 'Professor', 7, 1),
(6, 'Lisbon', 7, 2),
(7, 'Berlin', 1, 1),
(7, 'Professor', 7, 1);

-- =====================================================
-- End of Data Population
-- =====================================================