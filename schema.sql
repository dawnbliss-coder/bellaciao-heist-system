-- =====================================================
-- Operation Bella Ciao - Database Schema (CORRECTED)
-- Team: DnA_Not_Found (Team 54)
-- =====================================================

DROP DATABASE IF EXISTS bellaciao_db;
CREATE DATABASE bellaciao_db;
USE bellaciao_db;

-- =====================================================
-- Strong Entity Tables
-- =====================================================

-- Table: HEIST_BLUEPRINT
CREATE TABLE HEIST_BLUEPRINT (
    BlueprintID INT PRIMARY KEY,
    LocationName VARCHAR(100) NOT NULL,
    ArchitectBlindspot VARCHAR(200)
);

-- Table: CREW_MEMBER
CREATE TABLE CREW_MEMBER (
    CodeName VARCHAR(50) PRIMARY KEY,
    HeistID INT NOT NULL,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Specialization VARCHAR(100) NOT NULL,
    LoyaltyScore INT NOT NULL CHECK (LoyaltyScore >= 0 AND LoyaltyScore <= 100)
);

-- Table: RESOURCE
CREATE TABLE RESOURCE (
    ResourceID INT PRIMARY KEY,
    Type VARCHAR(100) NOT NULL,
    CurrentQuantity INT NOT NULL CHECK (CurrentQuantity >= 0),
    CriticalThreshold INT NOT NULL CHECK (CriticalThreshold >= 0)
);

-- Table: POLICE_UNIT
CREATE TABLE POLICE_UNIT (
    UnitID INT PRIMARY KEY,
    CommanderName VARCHAR(100) NOT NULL,
    UnitType VARCHAR(100) NOT NULL,
    PredictableCounter INT CHECK (PredictableCounter >= 0 AND PredictableCounter <= 100),
    Morale INT CHECK (Morale >= 0 AND Morale <= 100)
);

-- Table: PLAN_PHASE (FIXED - column names match CHECK constraints)
CREATE TABLE PLAN_PHASE (
    PhaseID INT PRIMARY KEY,
    Phasecodename VARCHAR(100) NOT NULL UNIQUE,
    Planned_Duration INT NOT NULL CHECK (Planned_Duration > 0),
    Current_Dissonance INT DEFAULT 0 CHECK (Current_Dissonance >= 0)
);

-- Table: HOSTAGE (depends on CREW_MEMBER and HEIST_BLUEPRINT)
CREATE TABLE HOSTAGE (
    HostageID INT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Status ENUM('Cooperative', 'Neutral', 'Resistant', 'Hostile') NOT NULL,
    Usefulness INT CHECK (Usefulness >= 0 AND Usefulness <= 10),
    InstigatorFlag BOOLEAN DEFAULT FALSE,
    ManagerCodename VARCHAR(50),
    BlueprintID INT,
    FOREIGN KEY (ManagerCodename) REFERENCES CREW_MEMBER(CodeName)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (BlueprintID) REFERENCES HEIST_BLUEPRINT(BlueprintID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- =====================================================
-- Multivalued Attribute Table
-- =====================================================

-- Table: TRAITS (multivalued attribute of CREW_MEMBER)
CREATE TABLE TRAITS (
    Crew_No VARCHAR(50),
    VolatileTraits VARCHAR(100) NOT NULL,
    PRIMARY KEY (Crew_No, VolatileTraits),
    FOREIGN KEY (Crew_No) REFERENCES CREW_MEMBER(CodeName)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: KEYRMS (multivalued attribute of HEIST_BLUEPRINT) - FIXED semicolon
CREATE TABLE KEYRMS (
    BlueprintID INT NOT NULL,
    Keyrooms VARCHAR(100) NOT NULL,
    PRIMARY KEY (BlueprintID, Keyrooms),
    FOREIGN KEY (BlueprintID) REFERENCES HEIST_BLUEPRINT(BlueprintID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================
-- Subclass Tables (ISA Hierarchy)
-- =====================================================

-- Table: STRATEGIC_CREW (subclass of CREW_MEMBER) - FIXED FK reference
CREATE TABLE STRATEGIC_CREW (
    Codename VARCHAR(50) PRIMARY KEY,
    SecurityClearanceLevel VARCHAR(50) NOT NULL,
    FOREIGN KEY (Codename) REFERENCES CREW_MEMBER(CodeName)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: TACTICAL_CREW (subclass of CREW_MEMBER) - FIXED FK reference
CREATE TABLE TACTICAL_CREW (
    Codename VARCHAR(50) PRIMARY KEY,
    WeaponProficiency VARCHAR(100) NOT NULL,
    FOREIGN KEY (Codename) REFERENCES CREW_MEMBER(CodeName)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: TECHNICAL_CREW (subclass of CREW_MEMBER) - FIXED FK reference
CREATE TABLE TECHNICAL_CREW (
    Codename VARCHAR(50) PRIMARY KEY,
    TechnicalCertification VARCHAR(100) NOT NULL,
    FOREIGN KEY (Codename) REFERENCES CREW_MEMBER(CodeName)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================
-- Weak Entity Tables
-- =====================================================

-- Table: PSYCHOLOGICAL_REPORT (weak entity, depends on CREW_MEMBER)
CREATE TABLE PSYCHOLOGICAL_REPORT (
    Crew_Member VARCHAR(50),
    ReportTimestamp DATETIME,
    Frequency ENUM('Low', 'Medium', 'High', 'Very High') NOT NULL,
    MoralCompromiseLog TEXT,
    PRIMARY KEY (Crew_Member, ReportTimestamp),
    FOREIGN KEY (Crew_Member) REFERENCES CREW_MEMBER(CodeName)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: HOSTAGE_LOG (weak entity, depends on HOSTAGE)
CREATE TABLE HOSTAGE_LOG (
    HostageID INT,
    Interaction_Timestamp DATETIME,
    Interacting_Crew VARCHAR(50) NOT NULL,
    Interaction_Type ENUM('Interrogation', 'Care', 'Monitoring', 'Confrontation', 'Negotiation', 'Psychological') NOT NULL,
    Summary TEXT,
    PRIMARY KEY (HostageID, Interaction_Timestamp),
    FOREIGN KEY (HostageID) REFERENCES HOSTAGE(HostageID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (Interacting_Crew) REFERENCES CREW_MEMBER(CodeName)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================
-- Binary Relationship Tables
-- =====================================================

-- Table: ASSIGNED_TO (CREW_MEMBER assigned to PLAN_PHASE) - FIXED PK column name
CREATE TABLE ASSIGNED_TO (
    Cname VARCHAR(50),
    Phase_id INT,
    PRIMARY KEY (Cname, Phase_id),
    FOREIGN KEY (Cname) REFERENCES CREW_MEMBER(CodeName)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (Phase_id) REFERENCES PLAN_PHASE(PhaseID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: MONITORS (POLICE_UNIT monitors HEIST_BLUEPRINT)
CREATE TABLE MONITORS (
    Unit_id INT,
    Bprint_id INT,
    PRIMARY KEY (Unit_id, Bprint_id),
    FOREIGN KEY (Unit_id) REFERENCES POLICE_UNIT(UnitID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (Bprint_id) REFERENCES HEIST_BLUEPRINT(BlueprintID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: REQUIRES (PLAN_PHASE requires RESOURCE)
CREATE TABLE REQUIRES (
    Phase INT,
    Res_id INT,
    PRIMARY KEY (Phase, Res_id),
    FOREIGN KEY (Phase) REFERENCES PLAN_PHASE(PhaseID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (Res_id) REFERENCES RESOURCE(ResourceID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: DEVIATES_FROM (CREW_MEMBER deviates from PLAN_PHASE) - FIXED FK reference
CREATE TABLE DEVIATES_FROM (
    C_id VARCHAR(50),
    P_id INT,
    PRIMARY KEY (C_id, P_id),
    FOREIGN KEY (C_id) REFERENCES CREW_MEMBER(CodeName)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (P_id) REFERENCES PLAN_PHASE(PhaseID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: COMMUNICATES_WITH (CREW_MEMBER communicates with POLICE_UNIT) - FIXED FK reference
CREATE TABLE COMMUNICATES_WITH (
    Codeid VARCHAR(50),
    Uid INT,
    PRIMARY KEY (Codeid, Uid),
    FOREIGN KEY (Codeid) REFERENCES CREW_MEMBER(CodeName)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (Uid) REFERENCES POLICE_UNIT(UnitID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: IS_LOCATED_IN (HOSTAGE is located in HEIST_BLUEPRINT)
CREATE TABLE IS_LOCATED_IN (
    h_id INT,
    BPid INT,
    PRIMARY KEY (h_id, BPid),
    FOREIGN KEY (h_id) REFERENCES HOSTAGE(HostageID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (BPid) REFERENCES HEIST_BLUEPRINT(BlueprintID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================
-- N-ary Relationship Tables
-- =====================================================

-- Table: NEGOTIATION (4-way relationship)
CREATE TABLE NEGOTIATION (
    P_unit INT,
    crew_id VARCHAR(50),
    Hostageid INT,
    resource_id INT,
    PRIMARY KEY (P_unit, crew_id, Hostageid, resource_id),
    FOREIGN KEY (P_unit) REFERENCES POLICE_UNIT(UnitID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (crew_id) REFERENCES CREW_MEMBER(CodeName)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (Hostageid) REFERENCES HOSTAGE(HostageID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (resource_id) REFERENCES RESOURCE(ResourceID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: TASK_ASSIGNMENT (4-way relationship) - FIXED FK reference
CREATE TABLE TASK_ASSIGNMENT (
    PID INT,
    CName VARCHAR(50),
    ResID INT,
    BID INT,
    PRIMARY KEY (PID, CName, ResID, BID),
    FOREIGN KEY (PID) REFERENCES PLAN_PHASE(PhaseID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (CName) REFERENCES CREW_MEMBER(CodeName)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (ResID) REFERENCES RESOURCE(ResourceID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (BID) REFERENCES HEIST_BLUEPRINT(BlueprintID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- =====================================================
-- End of Schema
-- =====================================================