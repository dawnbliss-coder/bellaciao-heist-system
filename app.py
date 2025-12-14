from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from database import Database
from datetime import datetime
import csv
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key-for-development')

# Initialize database with environment variables
db = Database(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'bellaciao_db')
)

# ============================================================================
# DASHBOARD & HOME
# ============================================================================

@app.route('/')
def index():
    """Dashboard with overview statistics"""
    try:
        # Get crew count
        crew_count = db.execute_query("SELECT COUNT(*) as count FROM CREW_MEMBER")[0]['count']
        
        # Get hostage count
        hostage_count = db.execute_query("SELECT COUNT(*) as count FROM HOSTAGE")[0]['count']
        
        # Get active phases
        phase_count = db.execute_query("SELECT COUNT(*) as count FROM PLAN_PHASE")[0]['count']
        
        # Get critical resources
        critical_resources = db.execute_query("""
            SELECT COUNT(*) as count FROM RESOURCE 
            WHERE CurrentQuantity <= CriticalThreshold
        """)[0]['count']
        
        # DEBUG: Print to console
        print(f"DEBUG: crew={crew_count}, hostages={hostage_count}, phases={phase_count}, critical={critical_resources}")
        
        # Get loyalty distribution for chart
        loyalty_data = db.execute_query("""
            SELECT CodeName, LoyaltyScore FROM CREW_MEMBER 
            ORDER BY LoyaltyScore DESC LIMIT 10
        """)
        
        # Get hostage status distribution
        hostage_status = db.execute_query("""
            SELECT Status, COUNT(*) as count 
            FROM HOSTAGE 
            GROUP BY Status
        """)
        
        # Get phase progress
        phases = db.execute_query("""
            SELECT Phasecodename, Planned_Duration, Current_Dissonance 
            FROM PLAN_PHASE 
            ORDER BY PhaseID
        """)
        
        return render_template('index.html',
            crew_count=crew_count,
            hostage_count=hostage_count,
            phase_count=phase_count,
            critical_resources=critical_resources,
            loyalty_data=loyalty_data,
            hostage_status=hostage_status,
            phases=phases
        )
    except Exception as e:
        flash(f"Error loading dashboard: {str(e)}", "danger")
        return render_template('index.html', 
            crew_count=0, hostage_count=0, phase_count=0, critical_resources=0,
            loyalty_data=[], hostage_status=[], phases=[]
        )

# ============================================================================
# CREW MANAGEMENT
# ============================================================================

@app.route('/crew')
def crew_list():
    """List all crew members with their profiles"""
    try:
        crew = db.execute_query("""
            SELECT c.CodeName, c.FirstName, c.LastName, c.Specialization, 
                   c.LoyaltyScore, tc.WeaponProficiency,
                   sc.SecurityClearanceLevel, tech.TechnicalCertification
            FROM CREW_MEMBER c
            LEFT JOIN TACTICAL_CREW tc ON c.CodeName = tc.Codename
            LEFT JOIN STRATEGIC_CREW sc ON c.CodeName = sc.Codename
            LEFT JOIN TECHNICAL_CREW tech ON c.CodeName = tech.Codename
            ORDER BY c.LoyaltyScore DESC
        """)
        
        # Get traits for each crew member
        for member in crew:
            traits = db.execute_query("""
                SELECT VolatileTraits FROM TRAITS WHERE Crew_No = %s
            """, (member['CodeName'],))
            member['traits'] = [t['VolatileTraits'] for t in traits]
        
        return render_template('crew.html', crew=crew)
    except Exception as e:
        flash(f"Error loading crew: {str(e)}", "danger")
        return render_template('crew.html', crew=[])

@app.route('/crew/<codename>')
def crew_detail(codename):
    """Detailed view of a crew member"""
    try:
        member = db.execute_query("""
            SELECT c.*, tc.WeaponProficiency, sc.SecurityClearanceLevel, 
                   tech.TechnicalCertification
            FROM CREW_MEMBER c
            LEFT JOIN TACTICAL_CREW tc ON c.CodeName = tc.Codename
            LEFT JOIN STRATEGIC_CREW sc ON c.CodeName = sc.Codename
            LEFT JOIN TECHNICAL_CREW tech ON c.CodeName = tech.Codename
            WHERE c.CodeName = %s
        """, (codename,))[0]
        
        # Get assigned phases
        phases = db.execute_query("""
            SELECT pp.Phasecodename, pp.Planned_Duration
            FROM ASSIGNED_TO at
            JOIN PLAN_PHASE pp ON at.Phase_id = pp.PhaseID
            WHERE at.Cname = %s
        """, (codename,))
        
        # Get psychological reports
        reports = db.execute_query("""
            SELECT ReportTimestamp, Frequency, MoralCompromiseLog
            FROM PSYCHOLOGICAL_REPORT
            WHERE Crew_Member = %s
            ORDER BY ReportTimestamp DESC
        """, (codename,))
        
        # Get deviations
        deviations = db.execute_query("""
            SELECT pp.Phasecodename
            FROM DEVIATES_FROM df
            JOIN PLAN_PHASE pp ON df.P_id = pp.PhaseID
            WHERE df.C_id = %s
        """, (codename,))
        
        return render_template('crew_detail.html', 
            member=member, phases=phases, reports=reports, deviations=deviations
        )
    except Exception as e:
        flash(f"Error loading crew member: {str(e)}", "danger")
        return redirect(url_for('crew_list'))

# ============================================================================
# HOSTAGE MANAGEMENT
# ============================================================================

@app.route('/hostages')
def hostages_list():
    """List all hostages with their status"""
    try:
        hostages = db.execute_query("""
            SELECT h.*, hb.LocationName
            FROM HOSTAGE h
            LEFT JOIN IS_LOCATED_IN il ON h.HostageID = il.h_id
            LEFT JOIN HEIST_BLUEPRINT hb ON il.BPid = hb.BlueprintID
            ORDER BY h.Status, h.Usefulness DESC
        """)
        
        return render_template('hostages.html', hostages=hostages)
    except Exception as e:
        flash(f"Error loading hostages: {str(e)}", "danger")
        return render_template('hostages.html', hostages=[])

@app.route('/hostages/<int:hostage_id>')
def hostage_detail(hostage_id):
    """Detailed view of a hostage with interaction logs"""
    try:
        hostage = db.execute_query("""
            SELECT h.*, hb.LocationName
            FROM HOSTAGE h
            LEFT JOIN IS_LOCATED_IN il ON h.HostageID = il.h_id
            LEFT JOIN HEIST_BLUEPRINT hb ON il.BPid = hb.BlueprintID
            WHERE h.HostageID = %s
        """, (hostage_id,))[0]
        
        # Get interaction logs
        logs = db.execute_query("""
            SELECT Interaction_Timestamp, Interacting_Crew, 
                   Interaction_Type, Summary
            FROM HOSTAGE_LOG
            WHERE HostageID = %s
            ORDER BY Interaction_Timestamp DESC
        """, (hostage_id,))
        
        return render_template('hostage_detail.html', hostage=hostage, logs=logs)
    except Exception as e:
        flash(f"Error loading hostage: {str(e)}", "danger")
        return redirect(url_for('hostages_list'))

# ============================================================================
# RESOURCE MANAGEMENT
# ============================================================================

@app.route('/resources')
def resources_list():
    """List all resources with status indicators"""
    try:
        resources = db.execute_query("""
            SELECT * FROM RESOURCE ORDER BY Type
        """)
        
        # Calculate status for each resource
        for r in resources:
            if r['CurrentQuantity'] <= r['CriticalThreshold']:
                r['status'] = 'critical'
            elif r['CurrentQuantity'] <= r['CriticalThreshold'] * 2:
                r['status'] = 'warning'
            else:
                r['status'] = 'good'
        
        return render_template('resources.html', resources=resources)
    except Exception as e:
        flash(f"Error loading resources: {str(e)}", "danger")
        return render_template('resources.html', resources=[])

# ============================================================================
# PHASE MANAGEMENT
# ============================================================================

@app.route('/phases')
def phases_list():
    """List all plan phases with requirements"""
    try:
        phases = db.execute_query("""
            SELECT * FROM PLAN_PHASE ORDER BY PhaseID
        """)
        
        # Get requirements for each phase
        for phase in phases:
            requirements = db.execute_query("""
                SELECT r.ResourceID, r.Type, r.CurrentQuantity, r.CriticalThreshold
                FROM REQUIRES req
                JOIN RESOURCE r ON req.Res_id = r.ResourceID
                WHERE req.Phase = %s
            """, (phase['PhaseID'],))
            phase['requirements'] = requirements
            
            # Get assigned crew
            crew = db.execute_query("""
                SELECT cm.CodeName, cm.Specialization
                FROM ASSIGNED_TO at
                JOIN CREW_MEMBER cm ON at.Cname = cm.CodeName
                WHERE at.Phase_id = %s
            """, (phase['PhaseID'],))
            phase['crew'] = crew
        
        return render_template('phases.html', phases=phases)
    except Exception as e:
        flash(f"Error loading phases: {str(e)}", "danger")
        return render_template('phases.html', phases=[])

# ============================================================================
# API ENDPOINTS FOR CHARTS
# ============================================================================

@app.route('/api/loyalty-chart')
def api_loyalty_chart():
    """API endpoint for loyalty chart data"""
    try:
        data = db.execute_query("""
            SELECT CodeName, LoyaltyScore 
            FROM CREW_MEMBER 
            ORDER BY LoyaltyScore DESC
        """)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/resource-chart')
def api_resource_chart():
    """API endpoint for resource status chart"""
    try:
        data = db.execute_query("""
            SELECT Type, CurrentQuantity, CriticalThreshold 
            FROM RESOURCE
        """)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# CREW - ADD/EDIT/DELETE
# ============================================================================

@app.route('/crew/add', methods=['GET', 'POST'])
def crew_add():
    """Add new crew member"""
    if request.method == 'POST':
        try:
            codename = request.form['codename']
            heist_id = request.form['heist_id']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            specialization = request.form['specialization']
            loyalty_score = request.form['loyalty_score']
            
            db.execute_insert("""
                INSERT INTO CREW_MEMBER (CodeName, HeistID, FirstName, LastName, Specialization, LoyaltyScore)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (codename, heist_id, first_name, last_name, specialization, loyalty_score))
            
            flash(f'Crew member {codename} added successfully!', 'success')
            return redirect(url_for('crew_list'))
        except Exception as e:
            flash(f'Error adding crew member: {str(e)}', 'danger')
    
    return render_template('crew_add.html')

@app.route('/crew/edit/<codename>', methods=['GET', 'POST'])
def crew_edit(codename):
    """Edit existing crew member"""
    if request.method == 'POST':
        try:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            specialization = request.form['specialization']
            loyalty_score = request.form['loyalty_score']
            
            db.execute_update("""
                UPDATE CREW_MEMBER 
                SET FirstName = %s, LastName = %s, Specialization = %s, LoyaltyScore = %s
                WHERE CodeName = %s
            """, (first_name, last_name, specialization, loyalty_score, codename))
            
            flash(f'Crew member {codename} updated successfully!', 'success')
            return redirect(url_for('crew_list'))
        except Exception as e:
            flash(f'Error updating crew member: {str(e)}', 'danger')
    
    try:
        member = db.execute_query("""
            SELECT * FROM CREW_MEMBER WHERE CodeName = %s
        """, (codename,))[0]
        return render_template('crew_edit.html', member=member)
    except Exception as e:
        flash(f'Error loading crew member: {str(e)}', 'danger')
        return redirect(url_for('crew_list'))

@app.route('/crew/delete/<codename>', methods=['POST'])
def crew_delete(codename):
    """Delete crew member"""
    try:
        db.execute_delete("DELETE FROM CREW_MEMBER WHERE CodeName = %s", (codename,))
        flash(f'Crew member {codename} deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting crew member: {str(e)}', 'danger')
    return redirect(url_for('crew_list'))

# ============================================================================
# HOSTAGE - ADD/EDIT/DELETE
# ============================================================================

@app.route('/hostages/add', methods=['GET', 'POST'])
def hostage_add():
    """Add new hostage"""
    if request.method == 'POST':
        try:
            hostage_id = request.form['hostage_id']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            status = request.form['status']
            usefulness = request.form['usefulness']
            instigator = 'instigator' in request.form
            manager = request.form.get('manager') or None
            blueprint_id = request.form.get('blueprint_id') or None
            
            db.execute_insert("""
                INSERT INTO HOSTAGE (HostageID, FirstName, LastName, Status, Usefulness, InstigatorFlag, ManagerCodename, BlueprintID)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (hostage_id, first_name, last_name, status, usefulness, instigator, manager, blueprint_id))
            
            flash(f'Hostage {first_name} {last_name} added successfully!', 'success')
            return redirect(url_for('hostages_list'))
        except Exception as e:
            flash(f'Error adding hostage: {str(e)}', 'danger')
    
    # Get crew members for manager dropdown
    crew = db.execute_query("SELECT CodeName FROM CREW_MEMBER ORDER BY CodeName")
    blueprints = db.execute_query("SELECT BlueprintID, LocationName FROM HEIST_BLUEPRINT")
    return render_template('hostage_add.html', crew=crew, blueprints=blueprints)

@app.route('/hostages/edit/<int:hostage_id>', methods=['GET', 'POST'])
def hostage_edit(hostage_id):
    """Edit hostage status"""
    if request.method == 'POST':
        try:
            status = request.form['status']
            usefulness = request.form['usefulness']
            instigator = 'instigator' in request.form
            
            db.execute_update("""
                UPDATE HOSTAGE 
                SET Status = %s, Usefulness = %s, InstigatorFlag = %s
                WHERE HostageID = %s
            """, (status, usefulness, instigator, hostage_id))
            
            flash(f'Hostage #{hostage_id} updated successfully!', 'success')
            return redirect(url_for('hostages_list'))
        except Exception as e:
            flash(f'Error updating hostage: {str(e)}', 'danger')
    
    try:
        hostage = db.execute_query("SELECT * FROM HOSTAGE WHERE HostageID = %s", (hostage_id,))[0]
        return render_template('hostage_edit.html', hostage=hostage)
    except Exception as e:
        flash(f'Error loading hostage: {str(e)}', 'danger')
        return redirect(url_for('hostages_list'))

@app.route('/hostages/delete/<int:hostage_id>', methods=['POST'])
def hostage_delete(hostage_id):
    """Delete hostage"""
    try:
        db.execute_delete("DELETE FROM HOSTAGE WHERE HostageID = %s", (hostage_id,))
        flash(f'Hostage #{hostage_id} deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting hostage: {str(e)}', 'danger')
    return redirect(url_for('hostages_list'))

# ============================================================================
# RESOURCE - UPDATE QUANTITY
# ============================================================================

@app.route('/resources/update/<int:resource_id>', methods=['POST'])
def resource_update(resource_id):
    """Update resource quantity"""
    try:
        new_quantity = request.form['quantity']
        db.execute_update("""
            UPDATE RESOURCE SET CurrentQuantity = %s WHERE ResourceID = %s
        """, (new_quantity, resource_id))
        flash('Resource quantity updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating resource: {str(e)}', 'danger')
    return redirect(url_for('resources_list'))

# ============================================================================
# PHASE - ADD/DELETE
# ============================================================================

@app.route('/phases/add', methods=['GET', 'POST'])
def phase_add():
    """Add new phase"""
    if request.method == 'POST':
        try:
            phase_id = request.form['phase_id']
            codename = request.form['codename']
            duration = request.form['duration']
            dissonance = request.form.get('dissonance', 0)
            
            db.execute_insert("""
                INSERT INTO PLAN_PHASE (PhaseID, Phasecodename, Planned_Duration, Current_Dissonance)
                VALUES (%s, %s, %s, %s)
            """, (phase_id, codename, duration, dissonance))
            
            flash(f'Phase {codename} added successfully!', 'success')
            return redirect(url_for('phases_list'))
        except Exception as e:
            flash(f'Error adding phase: {str(e)}', 'danger')
    
    return render_template('phase_add.html')

@app.route('/phases/delete/<int:phase_id>', methods=['POST'])
def phase_delete(phase_id):
    """Delete phase"""
    try:
        db.execute_delete("DELETE FROM PLAN_PHASE WHERE PhaseID = %s", (phase_id,))
        flash(f'Phase deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting phase: {str(e)}', 'danger')
    return redirect(url_for('phases_list'))

# ============================================================================
# SEARCH & FILTER
# ============================================================================

@app.route('/crew/search')
def crew_search():
    """Search crew members"""
    query = request.args.get('q', '').strip()
    specialization = request.args.get('spec', '').strip()
    
    try:
        sql = """
            SELECT c.CodeName, c.FirstName, c.LastName, c.Specialization, 
                   c.LoyaltyScore, tc.WeaponProficiency
            FROM CREW_MEMBER c
            LEFT JOIN TACTICAL_CREW tc ON c.CodeName = tc.Codename
            WHERE 1=1
        """
        params = []
        
        if query:
            sql += " AND (c.CodeName LIKE %s OR c.FirstName LIKE %s OR c.LastName LIKE %s)"
            search_term = f"%{query}%"
            params.extend([search_term, search_term, search_term])
        
        if specialization:
            sql += " AND c.Specialization LIKE %s"
            params.append(f"%{specialization}%")
        
        sql += " ORDER BY c.LoyaltyScore DESC"
        
        crew = db.execute_query(sql, tuple(params) if params else None)
        
        # Get traits for each member
        for member in crew:
            traits = db.execute_query("SELECT VolatileTraits FROM TRAITS WHERE Crew_No = %s", (member['CodeName'],))
            member['traits'] = [t['VolatileTraits'] for t in traits]
        
        return render_template('crew.html', crew=crew, search_query=query, search_spec=specialization)
    except Exception as e:
        flash(f'Search error: {str(e)}', 'danger')
        return redirect(url_for('crew_list'))

@app.route('/hostages/filter')
def hostages_filter():
    """Filter hostages by status"""
    status = request.args.get('status', '').strip()
    
    try:
        if status:
            hostages = db.execute_query("""
                SELECT h.*, hb.LocationName
                FROM HOSTAGE h
                LEFT JOIN IS_LOCATED_IN il ON h.HostageID = il.h_id
                LEFT JOIN HEIST_BLUEPRINT hb ON il.BPid = hb.BlueprintID
                WHERE h.Status = %s
                ORDER BY h.Usefulness DESC
            """, (status,))
        else:
            return redirect(url_for('hostages_list'))
        
        return render_template('hostages.html', hostages=hostages, filter_status=status)
    except Exception as e:
        flash(f'Filter error: {str(e)}', 'danger')
        return redirect(url_for('hostages_list'))

# Add after your existing phase routes

@app.route('/phases/<int:phase_id>/assign-crew', methods=['GET', 'POST'])
def phase_assign_crew(phase_id):
    """Assign crew to a phase"""
    if request.method == 'POST':
        try:
            crew_codename = request.form['crew_codename']
            
            # Check if already assigned
            existing = db.execute_query("""
                SELECT * FROM ASSIGNED_TO WHERE Cname = %s AND Phase_id = %s
            """, (crew_codename, phase_id))
            
            if existing:
                flash('Crew member already assigned to this phase!', 'warning')
            else:
                db.execute_insert("""
                    INSERT INTO ASSIGNED_TO (Cname, Phase_id) VALUES (%s, %s)
                """, (crew_codename, phase_id))
                flash(f'Crew member {crew_codename} assigned successfully!', 'success')
            
            return redirect(url_for('phases_list'))
        except Exception as e:
            flash(f'Error assigning crew: {str(e)}', 'danger')
    
    try:
        # Get phase details
        phase = db.execute_query("SELECT * FROM PLAN_PHASE WHERE PhaseID = %s", (phase_id,))[0]
        
        # Get available crew (not yet assigned to this phase)
        crew = db.execute_query("""
            SELECT CodeName, FirstName, LastName, Specialization
            FROM CREW_MEMBER
            WHERE CodeName NOT IN (
                SELECT Cname FROM ASSIGNED_TO WHERE Phase_id = %s
            )
            ORDER BY CodeName
        """, (phase_id,))
        
        return render_template('phase_assign_crew.html', phase=phase, crew=crew)
    except Exception as e:
        flash(f'Error loading assignment page: {str(e)}', 'danger')
        return redirect(url_for('phases_list'))

@app.route('/phases/<int:phase_id>/assign-resource', methods=['GET', 'POST'])
def phase_assign_resource(phase_id):
    """Assign resource to a phase"""
    if request.method == 'POST':
        try:
            resource_id = request.form['resource_id']
            
            # Check if already assigned
            existing = db.execute_query("""
                SELECT * FROM REQUIRES WHERE Phase = %s AND Res_id = %s
            """, (phase_id, resource_id))
            
            if existing:
                flash('Resource already assigned to this phase!', 'warning')
            else:
                db.execute_insert("""
                    INSERT INTO REQUIRES (Phase, Res_id) VALUES (%s, %s)
                """, (phase_id, resource_id))
                flash('Resource assigned successfully!', 'success')
            
            return redirect(url_for('phases_list'))
        except Exception as e:
            flash(f'Error assigning resource: {str(e)}', 'danger')
    
    try:
        # Get phase details
        phase = db.execute_query("SELECT * FROM PLAN_PHASE WHERE PhaseID = %s", (phase_id,))[0]
        
        # Get available resources (not yet assigned to this phase)
        resources = db.execute_query("""
            SELECT ResourceID, Type, CurrentQuantity
            FROM RESOURCE
            WHERE ResourceID NOT IN (
                SELECT Res_id FROM REQUIRES WHERE Phase = %s
            )
            ORDER BY Type
        """, (phase_id,))
        
        return render_template('phase_assign_resource.html', phase=phase, resources=resources)
    except Exception as e:
        flash(f'Error loading assignment page: {str(e)}', 'danger')
        return redirect(url_for('phases_list'))

@app.route('/phases/<int:phase_id>/remove-crew/<codename>', methods=['POST'])
def phase_remove_crew(phase_id, codename):
    """Remove crew from phase"""
    try:
        db.execute_delete("""
            DELETE FROM ASSIGNED_TO WHERE Cname = %s AND Phase_id = %s
        """, (codename, phase_id))
        flash(f'Crew member {codename} removed from phase!', 'success')
    except Exception as e:
        flash(f'Error removing crew: {str(e)}', 'danger')
    return redirect(url_for('phases_list'))

@app.route('/phases/<int:phase_id>/remove-resource/<int:resource_id>', methods=['POST'])
def phase_remove_resource(phase_id, resource_id):
    """Remove resource from phase"""
    try:
        db.execute_delete("""
            DELETE FROM REQUIRES WHERE Phase = %s AND Res_id = %s
        """, (phase_id, resource_id))
        flash('Resource removed from phase!', 'success')
    except Exception as e:
        flash(f'Error removing resource: {str(e)}', 'danger')
    return redirect(url_for('phases_list'))

# ============================================================================
# EXPORT TO CSV
# ============================================================================

@app.route('/export/crew')
def export_crew():
    """Export crew list to CSV"""
    try:
        crew = db.execute_query("""
            SELECT CodeName, FirstName, LastName, Specialization, LoyaltyScore
            FROM CREW_MEMBER
            ORDER BY LoyaltyScore DESC
        """)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['CodeName', 'FirstName', 'LastName', 'Specialization', 'LoyaltyScore'])
        
        for member in crew:
            writer.writerow([
                member['CodeName'],
                member['FirstName'],
                member['LastName'],
                member['Specialization'],
                member['LoyaltyScore']
            ])
        
        # Create response
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'crew_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    except Exception as e:
        flash(f'Export error: {str(e)}', 'danger')
        return redirect(url_for('crew_list'))

@app.route('/export/hostages')
def export_hostages():
    """Export hostages to CSV"""
    try:
        hostages = db.execute_query("""
            SELECT HostageID, FirstName, LastName, Status, Usefulness, ManagerCodename
            FROM HOSTAGE
            ORDER BY Status
        """)
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['HostageID', 'FirstName', 'LastName', 'Status', 'Usefulness', 'Manager'])
        
        for h in hostages:
            writer.writerow([
                h['HostageID'],
                h['FirstName'],
                h['LastName'],
                h['Status'],
                h['Usefulness'],
                h['ManagerCodename'] or 'None'
            ])
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'hostages_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    except Exception as e:
        flash(f'Export error: {str(e)}', 'danger')
        return redirect(url_for('hostages_list'))

@app.route('/export/resources')
def export_resources():
    """Export resources to CSV"""
    try:
        resources = db.execute_query("SELECT * FROM RESOURCE ORDER BY Type")
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ResourceID', 'Type', 'CurrentQuantity', 'CriticalThreshold'])
        
        for r in resources:
            writer.writerow([
                r['ResourceID'],
                r['Type'],
                r['CurrentQuantity'],
                r['CriticalThreshold']
            ])
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'resources_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    except Exception as e:
        flash(f'Export error: {str(e)}', 'danger')
        return redirect(url_for('resources_list'))

@app.route('/resources/add', methods=['GET', 'POST'])
def resource_add():
    """Add new resource"""
    if request.method == 'POST':
        try:
            # NO resource_id - auto-generated
            resource_type = request.form['type']
            current_quantity = request.form['current_quantity']
            critical_threshold = request.form['critical_threshold']
            
            # INSERT without ResourceID
            db.execute_insert("""
                INSERT INTO RESOURCE (Type, CurrentQuantity, CriticalThreshold)
                VALUES (%s, %s, %s)
            """, (resource_type, current_quantity, critical_threshold))
            
            flash(f'Resource "{resource_type}" added successfully!', 'success')
            return redirect(url_for('resources_list'))
        except Exception as e:
            flash(f'Error adding resource: {str(e)}', 'danger')
    
    return render_template('resource_add.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
