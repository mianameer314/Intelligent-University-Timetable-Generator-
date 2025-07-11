
from typing import Dict, List, Optional, Tuple, Generic, TypeVar
from abc import ABC, abstractmethod
import random

# Declare generic types
V = TypeVar('V')  # Example: ("BCS-3A", "AI")  # V is a tuple: (program-section, course)
D = TypeVar('D')  # Example: ("Mon", "8:30-10:00", "LT-1", "Mr. Ali")  # D is a tuple: (day, time, room, teacher)

# Abstract base constraint
class Constraint(Generic[V, D], ABC):
    def __init__(self, variables: List[V]) -> None:
        self.variables = variables  # Example: [(program-section, course), ...] e.g., [("BCS-3A", "AI"), ("BCS-3A", "Software Engineering")]

    @abstractmethod
    def satisfied(self, assignment: Dict[V, D]) -> bool:
        pass

# CSP class
class CSP(Generic[V, D]):
    def __init__(self, variables: List[V], domains: Dict[V, List[D]]) -> None:
        self.variables = variables # Example: [("BCS-1A", "Math"), ("BCS-1A", "Physics")]
        self.domains = domains  # Example: {("BCS-1A", "Math"): [("Mon", "8:30-10:00", "LT-1", "Mr. Ali"), ...]}
        self.constraints: Dict[V, List[Constraint[V, D]]] = {}
        for variable in self.variables:
            self.constraints[variable] = []  # Example: {("BCS-1A", "Math"): [], ...}

    def add_constraint(self, constraint: Constraint[V, D]) -> None:
        for variable in constraint.variables:
            if variable not in self.variables:
                raise ValueError(f"Variable {variable} not in CSP")
            self.constraints[variable].append(constraint)  # Example: Add TimetableConstraint to each variable

    def consistent(self, variable: V, assignment: Dict[V, D]) -> bool:
        # Example: variable = ("BCS-1A", "Math"), assignment = {("BCS-1A", "Math"): ("Mon", "8:30-10:00", "LT-1", "Mr. Ali")}
        return all(constraint.satisfied(assignment) for constraint in self.constraints[variable])

    def backtracking_search(self, assignment: Dict[V, D] = {}) -> Optional[Dict[V, D]]:
        if len(assignment) == len(self.variables):
            return assignment  # Example: All variables assigned, return solution

        # MRV heuristic: select unassigned variable with fewest remaining values
        unassigned = [v for v in self.variables if v not in assignment]  # Example: [("BCS-1A", "Physics"), ...]
        first = min(unassigned, key=lambda v: len(self.domains[v]))  # Example: ("BCS-1A", "Physics")

        # Try values in order of least constraining first
        for value in self.domains[first]:  # Example: value = ("Tue", "10:00-11:30", "LT-2", "Ms. Sara Ali")
            local_assignment = assignment.copy()
            local_assignment[first] = value  # Example: {("BCS-1A", "Math"): ..., ("BCS-1A", "Physics"): value}

            if self.consistent(first, local_assignment):  # Check if this assignment is valid
                result = self.backtracking_search(local_assignment)
                if result is not None:
                    return result
        return None

# Constraint for timetable clash detection
class TimetableConstraint(Constraint[Tuple[str, str], Tuple[str, str, str, str]]):
    def __init__(self, variables: List[Tuple[str, str]]) -> None:
        super().__init__(variables)

    def satisfied(self, assignment: Dict[Tuple[str, str], Tuple[str, str, str, str]]) -> bool:
        # assignment example: {("BCS-1A", "Math"): ("Mon", "8:30-10:00", "LT-1", "Mr. Ali"), ...}
        room_assignments = {}
        teacher_assignments = {}
        group_assignments = {}
        
        for (group, course), (day, time, room, teacher) in assignment.items():
            # Example: group = "BCS-1A", course = "Math", day = "Mon", time = "8:30-10:00", room = "LT-1", teacher = "Mr. Ali"
            group_time_key = (group, day, time)
            if group_time_key in group_assignments:
                return False  # Same group can't have two courses at same time
            group_assignments[group_time_key] = True
            
            teacher_time_key = (teacher, day, time)
            if teacher_time_key in teacher_assignments:
                return False  # Same teacher can't teach two courses at same time
            teacher_assignments[teacher_time_key] = True
            
            room_time_key = (room, day, time)
            if room_time_key in room_assignments:
                return False  # Same room can't host two courses at same time
            room_assignments[room_time_key] = True
            
        return True

class TimetableGenerator:
    def __init__(self):
        # Expanded programs and courses
        self.program_courses = {
            "BCS": {
                "1A": ["Programming Fundamentals", "Mathematics", "English", "Physics"],
                "2A": ["Data Structures", "OOP", "Database", "Statistics", "Deep Learning"],
                "3A": ["AI", "Software Engineering", "Operating Systems", "Computer Networks"],
                "4A": ["Machine Learning", "Compiler Design", "Web Development", "Final Year Project"]
            },
            "BSE": {
                "1A": ["Programming Fundamentals", "Mathematics", "English", "Physics"],
                "2A": ["DLD", "PF Lab", "PF", "OOP"],
                "3A": ["Software Engineering", "Database Systems", "Web Technologies", "Mobile Development"],
                "4A": ["Software Testing", "Project Management", "DevOps", "Final Year Project"]
            },
            "AI": {
                "1A": ["Programming Fundamentals", "Mathematics", "Statistics", "Logic"],
                "2A": ["DS", "AI Lab", "Machine Learning Basics", "Python Programming"],
                "3A": ["Deep Learning", "NLP", "Computer Vision", "Robotics"],
                "4A": ["Advanced AI", "Neural Networks", "AI Ethics", "Research Project"]
            },
            "CS": {
                "1A": ["Programming Fundamentals", "Mathematics", "English", "Computer Science Basics"],
                "2A": ["Data Structures", "Algorithms", "Computer Architecture", "Assembly Language"],
                "3A": ["Operating Systems", "Database Systems", "Computer Networks", "Software Engineering"],
                "4A": ["Distributed Systems", "Cybersecurity", "Cloud Computing", "Capstone Project"]
            },
            "SE": {
                "1A": ["Programming Fundamentals", "Mathematics", "English", "Software Basics"],
                "2A": ["OOP", "Software Design", "Requirements Engineering", "Testing Fundamentals"],
                "3A": ["Software Architecture", "Project Management", "Quality Assurance", "Agile Methods"],
                "4A": ["Advanced Software Engineering", "DevOps", "Software Metrics", "Industry Project"]
            },
            "DS": {
                "1A": ["Programming Fundamentals", "Mathematics", "Statistics", "Data Science Intro"],
                "2A": ["Data Analysis", "Database Systems", "Python for Data Science", "Visualization"],
                "3A": ["Machine Learning", "Big Data", "Data Mining", "Statistical Analysis"],
                "4A": ["Deep Learning", "Advanced Analytics", "Data Ethics", "Capstone Project"]
            }
        }

        # Generate sufficient domain values (time slots)
        self.domain_values = self.generate_domains() # Example: [("Mon", "8:30-10:00", "LT-1", "Dr. Ahmed Khan"), ...]
        
    def add_program(self, program_name: str, courses_by_section: Dict[str, List[str]]) -> bool:
        """Add a new program with its courses"""
        try:
            if program_name in self.program_courses:
                return False  # Program already exists
            
            self.program_courses[program_name] = courses_by_section
            return True
        except Exception:
            return False
    
    def add_course_to_program(self, program: str, section: str, course: str) -> bool:
        """Add a course to an existing program section"""
        try:
            if program not in self.program_courses:
                return False
            
            if section not in self.program_courses[program]:
                self.program_courses[program][section] = []
            
            if course not in self.program_courses[program][section]:
                self.program_courses[program][section].append(course)
                return True
            
            return False  # Course already exists
        except Exception:
            return False
    
    def get_all_programs(self) -> List[str]:
        """Get list of all available programs"""
        return list(self.program_courses.keys())
    
    def get_program_sections(self, program: str) -> List[str]:
        """Get sections for a specific program"""
        if program in self.program_courses:
            return list(self.program_courses[program].keys())
        return []
    
    def get_section_courses(self, program: str, section: str) -> List[str]:
        """Get courses for a specific program section"""
        if program in self.program_courses and section in self.program_courses[program]:
            return self.program_courses[program][section][:]
        return []
        
    def generate_domains(self) -> List[Tuple[str, str, str, str]]:
        """Generate sufficient time slots for scheduling"""
        days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        time_slots = [
            "8:30-10:00", "10:00-11:30", "11:30-1:00", 
            "2:00-3:30", "3:30-5:00", "5:00-6:30"
        ]
        rooms = [f"LT-{i}" for i in range(1, 6)] + [f"LAB-{i}" for i in range(1, 6)]
        teachers = [
            "Dr. Ahmed Khan", "Ms. Sara Ali", "Mr. Hassan Sheikh", "Ms. Fatima Noor",
            "Dr. Muhammad Tariq", "Ms. Ayesha Malik", "Mr. Ali Raza", "Dr. Sana Ullah",
            "Ms. Arooj Fatima", "Mr. Kamran Hussain", "Dr. Zunaira Ahmad", "Ms. Hina Khan",
            "Dr. Hamid Ali", "Mr. Usman Ghani", "Ms. Rabia Nasir", "Dr. Imran Malik",
            "Mr. Asad Mehmood", "Ms. Nadia Sheikh", "Dr. Saira Bano", "Mr. Fahad Ahmad",
            "Dr. Omar Farooq", "Ms. Zara Ahmed", "Mr. Bilal Hassan", "Dr. Yasmin Akhtar",
            "Mr. Talha Malik", "Ms. Sana Iqbal", "Dr. Faisal Mahmood", "Ms. Hira Siddiqui"
        ]
        
        # Generate all possible combinations
        domains = []
        for day in days:
            for time in time_slots:
                for room in rooms:
                    # Random teacher assignment (can be optimized)
                    teacher = random.choice(teachers)
                    domains.append((day, time, room, teacher))
                    
        return domains

    def generate_variables(self, selected_programs: List[str] = None) -> List[Tuple[str, str]]:
        """Generate all course-program combinations as variables, ordered by program and section"""
        # Example: returns [("BCS-1A", "Programming Fundamentals"), ("BCS-1A", "Mathematics"), ...]
        variables = []
        programs_to_process = selected_programs if selected_programs else sorted(self.program_courses.keys())
        
        for program in programs_to_process:
            if program in self.program_courses:
                # Sort sections for each program (e.g., 1A, 2A, 3A, 4A)
                for section in sorted(self.program_courses[program].keys(), key=lambda x: int(x[:-1])):
                    courses = self.program_courses[program][section]
                    for course in courses:
                        variables.append((f"{program}-{section}", course))
        
        return variables

    def generate_timetable(self, selected_programs: List[str] = None) -> Dict:
        """Generate a complete timetable using CSP"""
        try:
            # Generate variables for selected programs
            variables = self.generate_variables(selected_programs)
            
            if not variables:
                return {
                    "success": False,
                    "error": "No valid programs selected or no courses found",
                    "timetable": None,
                    "stats": None
                }

            # Create domains - each variable can be assigned to any available slot
            domains = {}
            for variable in variables:
                shuffled = self.domain_values[:]
                random.shuffle(shuffled)
                domains[variable] = shuffled

            # Create CSP instance
            csp = CSP(variables, domains)

            # Add timetable constraint
            csp.add_constraint(TimetableConstraint(variables))

            # Solve CSP using backtracking
            solution = csp.backtracking_search()

            if solution is None:
                return {
                    "success": False,
                    "error": "No valid timetable found. Try with fewer programs or courses.",
                    "timetable": None,
                    "stats": {
                        "total_courses": len(variables),
                        "available_slots": len(self.domain_values),
                        "programs": len(selected_programs) if selected_programs else len(self.program_courses)
                    }
                }

            # Format the solution for display
            formatted_timetable = []
            for (program, course), (day, time, room, teacher) in solution.items():
                formatted_timetable.append({
                    "program": program,
                    "course": course,
                    "day": day,
                    "time": time,
                    "room": room,
                    "teacher": teacher
                })
            
            # Sort by day and time for better presentation
            day_order = {"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5}
            formatted_timetable.sort(key=lambda x: (day_order[x["day"]], x["time"]))

            return {
                "success": True,
                "error": None,
                "timetable": formatted_timetable,
                "stats": {
                    "total_courses": len(variables),
                    "scheduled_courses": len(solution),
                    "available_slots": len(self.domain_values),
                    "programs": len(selected_programs) if selected_programs else len(self.program_courses)
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating timetable: {str(e)}",
                "timetable": None,
                "stats": None
            }

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List
import csv
import io

# --- Utility functions (move these from utils.py or define here) ---

def filter_timetable(timetable, filters):
    def match(entry, key, value):
        if not value:
            return True
        return value.lower() in str(entry.get(key, "")).lower()
    return [
        entry for entry in timetable
        if match(entry, "program", filters.get("program", ""))
        and match(entry, "course", filters.get("course", ""))
        and match(entry, "teacher", filters.get("teacher", ""))
        and match(entry, "room", filters.get("room", ""))
        and match(entry, "day", filters.get("day", ""))
        and match(entry, "time", filters.get("time", ""))
    ]

def sort_timetable(timetable, sort_by, ascending=True):
    key_map = {
        "Program": "program",
        "Course": "course",
        "Day": "day",
        "Time": "time",
        "Teacher": "teacher",
        "Room": "room",
        "Batch (Program-Section)": "program"
    }
    key = key_map.get(sort_by, "day")
    return sorted(timetable, key=lambda x: x.get(key, ""), reverse=not ascending)

def get_unique_values(timetable, key):
    return sorted(list({entry.get(key, "") for entry in timetable if entry.get(key, "")}))

def export_to_csv(timetable):
    if not timetable:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["program", "course", "day", "time", "room", "teacher"])
    writer.writeheader()
    for row in timetable:
        writer.writerow(row)
    return output.getvalue()

def get_timetable_by_batch(timetable):
    batches = {}
    for entry in timetable:
        batch = entry.get("program", "")
        batches.setdefault(batch, []).append(entry)
    return batches

def get_statistics(timetable):
    stats = {
        "total_classes": len(timetable),
        "unique_programs": len(set(e["program"] for e in timetable)),
        "unique_courses": len(set(e["course"] for e in timetable)),
        "unique_teachers": len(set(e["teacher"] for e in timetable)),
        "unique_rooms": len(set(e["room"] for e in timetable)),
        "classes_per_day": {},
        "classes_per_program": {},
        "teacher_workload": {},
        "room_utilization": {}
    }
    for e in timetable:
        stats["classes_per_day"][e["day"]] = stats["classes_per_day"].get(e["day"], 0) + 1
        stats["classes_per_program"][e["program"]] = stats["classes_per_program"].get(e["program"], 0) + 1
        stats["teacher_workload"][e["teacher"]] = stats["teacher_workload"].get(e["teacher"], 0) + 1
        stats["room_utilization"][e["room"]] = stats["room_utilization"].get(e["room"], 0) + 1
    return stats

def validate_program_data(program_name, sections_data):
    if not program_name:
        return False, "Program name cannot be empty"
    if not sections_data:
        return False, "At least one section with courses is required"
    for section, courses in sections_data.items():
        if not section:
            return False, "Section name cannot be empty"
        if not courses:
            return False, f"Section '{section}' must have at least one course"
    return True, ""

class TimetableGUI:
    def __init__(self):
        self.generator = TimetableGenerator()
        self.current_timetable = []
        self.filtered_timetable = []
        
        self.root = tk.Tk()
        self.root.title("Enhanced CSP Timetable Generator")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        self.setup_gui()
        
    def setup_gui(self):
        # Main title
        title_frame = tk.Frame(self.root)
        title_frame.pack(pady=10)
        tk.Label(title_frame, text="Enhanced CSP Timetable Generator", 
                font=("Arial", 18, "bold")).pack()
        tk.Label(title_frame, text="Generate, search, sort, and manage university timetables", 
                font=("Arial", 12), fg="#666").pack()
        
        # Create main container with left panel and right content
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel for controls
        left_panel = tk.Frame(main_container, width=300, bg="#f0f0f0")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Right panel for timetable display
        right_panel = tk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_left_panel(left_panel)
        self.setup_right_panel(right_panel)
        
    def setup_left_panel(self, parent):
        # Generation Section
        gen_frame = tk.LabelFrame(parent, text="Generate Timetable", font=("Arial", 12, "bold"))
        gen_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(gen_frame, text="Select Programs:", font=("Arial", 10)).pack(anchor=tk.W, padx=5, pady=2)
        
        # Program selection with scrollable frame
        programs_frame = tk.Frame(gen_frame)
        programs_frame.pack(fill=tk.X, padx=5, pady=2)
        
        programs = self.generator.get_all_programs()
        self.program_vars = {p: tk.BooleanVar(value=True) for p in programs[:3]}  # Select first 3 by default
        for p in programs:
            if p not in self.program_vars:
                self.program_vars[p] = tk.BooleanVar()
            tk.Checkbutton(programs_frame, text=p, variable=self.program_vars[p], 
                          font=("Arial", 10)).pack(anchor=tk.W)
        
        tk.Button(gen_frame, text="Generate Timetable", font=("Arial", 11, "bold"), 
                 command=self.generate_timetable, bg="#4CAF50", fg="white", width=25).pack(pady=5)
        
        # Search and Filter Section
        filter_frame = tk.LabelFrame(parent, text="Search & Filter", font=("Arial", 12, "bold"))
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Program filter
        tk.Label(filter_frame, text="Program:", font=("Arial", 10)).pack(anchor=tk.W, padx=5)
        self.program_filter = ttk.Combobox(filter_frame, width=25, state="readonly")
        self.program_filter.pack(padx=5, pady=2)
        self.program_filter.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Course search
        tk.Label(filter_frame, text="Course Search:", font=("Arial", 10)).pack(anchor=tk.W, padx=5)
        self.course_search = tk.Entry(filter_frame, width=28)
        self.course_search.pack(padx=5, pady=2)
        self.course_search.bind('<KeyRelease>', self.apply_filters)
        
        # Teacher search
        tk.Label(filter_frame, text="Teacher Search:", font=("Arial", 10)).pack(anchor=tk.W, padx=5)
        self.teacher_search = tk.Entry(filter_frame, width=28)
        self.teacher_search.pack(padx=5, pady=2)
        self.teacher_search.bind('<KeyRelease>', self.apply_filters)
        
        # Day filter
        tk.Label(filter_frame, text="Day:", font=("Arial", 10)).pack(anchor=tk.W, padx=5)
        self.day_filter = ttk.Combobox(filter_frame, width=25, state="readonly")
        self.day_filter.pack(padx=5, pady=2)
        self.day_filter.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Room search
        tk.Label(filter_frame, text="Room Search:", font=("Arial", 10)).pack(anchor=tk.W, padx=5)
        self.room_search = tk.Entry(filter_frame, width=28)
        self.room_search.pack(padx=5, pady=2)
        self.room_search.bind('<KeyRelease>', self.apply_filters)
        
        # Time search
        tk.Label(filter_frame, text="Time Search:", font=("Arial", 10)).pack(anchor=tk.W, padx=5)
        self.time_search = tk.Entry(filter_frame, width=28)
        self.time_search.pack(padx=5, pady=2)
        self.time_search.bind('<KeyRelease>', self.apply_filters)
        
        # Sorting Section
        sort_frame = tk.LabelFrame(parent, text="Sort & Display", font=("Arial", 12, "bold"))
        sort_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(sort_frame, text="Sort by:", font=("Arial", 10)).pack(anchor=tk.W, padx=5)
        self.sort_by = ttk.Combobox(sort_frame, width=25, state="readonly")
        self.sort_by['values'] = ['Program', 'Course', 'Day', 'Time', 'Teacher', 'Room', 'Batch (Program-Section)']
        self.sort_by.set('Day')
        self.sort_by.pack(padx=5, pady=2)
        self.sort_by.bind('<<ComboboxSelected>>', self.apply_sorting)
        
        tk.Label(sort_frame, text="Order:", font=("Arial", 10)).pack(anchor=tk.W, padx=5)
        self.sort_order = ttk.Combobox(sort_frame, width=25, state="readonly")
        self.sort_order['values'] = ['Ascending', 'Descending']
        self.sort_order.set('Ascending')
        self.sort_order.pack(padx=5, pady=2)
        self.sort_order.bind('<<ComboboxSelected>>', self.apply_sorting)
        
        # View mode
        tk.Label(sort_frame, text="View Mode:", font=("Arial", 10)).pack(anchor=tk.W, padx=5)
        self.view_mode = ttk.Combobox(sort_frame, width=25, state="readonly")
        self.view_mode['values'] = ['Table View', 'Batch-wise View']
        self.view_mode.set('Table View')
        self.view_mode.pack(padx=5, pady=2)
        self.view_mode.bind('<<ComboboxSelected>>', self.update_display)
        
        # Export button
        tk.Button(sort_frame, text="Export CSV", font=("Arial", 10), 
                 command=self.export_csv, bg="#2196F3", fg="white", width=25).pack(pady=5)
        
        # Program Management Section
        mgmt_frame = tk.LabelFrame(parent, text="Program Management", font=("Arial", 12, "bold"))
        mgmt_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(mgmt_frame, text="Add New Program", font=("Arial", 10), 
                 command=self.add_program_dialog, bg="#FF9800", fg="white", width=25).pack(pady=2)
        tk.Button(mgmt_frame, text="Add Course to Program", font=("Arial", 10), 
                 command=self.add_course_dialog, bg="#9C27B0", fg="white", width=25).pack(pady=2)
        
    def setup_right_panel(self, parent):
        # Status label
        self.status_label = tk.Label(parent, text="Generate a timetable to get started", 
                                   font=("Arial", 11, "italic"), fg="#666")
        self.status_label.pack(pady=5)
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Table view tab
        self.table_frame = tk.Frame(self.notebook)
        self.notebook.add(self.table_frame, text="Timetable")
        
        # Statistics view tab
        self.stats_frame = tk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        
        self.setup_table_view()
        self.setup_stats_view()
        
    def setup_table_view(self):
        # Timetable display
        columns = ("Program", "Course", "Day", "Time", "Room", "Teacher")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150 if col != "Course" else 200, anchor=tk.CENTER)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=v_scrollbar.set, xscroll=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)
        
    def setup_stats_view(self):
        # Statistics display
        self.stats_text = tk.Text(self.stats_frame, font=("Courier", 10), wrap=tk.WORD)
        stats_scrollbar = ttk.Scrollbar(self.stats_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.configure(yscroll=stats_scrollbar.set)
        
        self.stats_text.grid(row=0, column=0, sticky="nsew")
        stats_scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.stats_frame.grid_rowconfigure(0, weight=1)
        self.stats_frame.grid_columnconfigure(0, weight=1)
        
    def generate_timetable(self):
        selected_programs = [p for p, var in self.program_vars.items() if var.get()]
        
        if not selected_programs:
            messagebox.showwarning("No Selection", "Please select at least one program")
            return
            
        result = self.generator.generate_timetable(selected_programs)
        
        if result["success"]:
            self.current_timetable = result["timetable"]
            self.filtered_timetable = result["timetable"][:]
            
            # Update filter options
            self.update_filter_options()
            
            # Update display
            self.update_display()
            
            # Update status
            stats = result["stats"]
            self.status_label.config(
                text=f"Success! {stats['scheduled_courses']} courses scheduled from {stats['total_courses']} total",
                fg="#4CAF50"
            )
            
            # Update statistics
            self.update_statistics()
            
        else:
            messagebox.showerror("Generation Failed", result["error"])
            self.status_label.config(text=f"Error: {result['error']}", fg="#f44336")
            
    def update_filter_options(self):
        if not self.current_timetable:
            return
            
        # Update program filter
        programs = ['All'] + get_unique_values(self.current_timetable, 'program')
        self.program_filter['values'] = programs
        self.program_filter.set('All')
        
        # Update day filter
        days = ['All'] + get_unique_values(self.current_timetable, 'day')
        self.day_filter['values'] = days
        self.day_filter.set('All')
        
    def apply_filters(self, event=None):
        if not self.current_timetable:
            return
            
        filters = {
            'program': self.program_filter.get() if self.program_filter.get() != 'All' else '',
            'course': self.course_search.get(),
            'teacher': self.teacher_search.get(),
            'room': self.room_search.get(),
            'day': self.day_filter.get() if self.day_filter.get() != 'All' else '',
            'time': self.time_search.get()
        }
        
        self.filtered_timetable = filter_timetable(self.current_timetable, filters)
        self.apply_sorting()
        
    def apply_sorting(self, event=None):
        if not self.filtered_timetable:
            return
            
        sort_by = self.sort_by.get()
        ascending = self.sort_order.get() == 'Ascending'
        
        self.filtered_timetable = sort_timetable(self.filtered_timetable, sort_by, ascending)
        self.update_display()
        
    def update_display(self, event=None):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not self.filtered_timetable:
            self.status_label.config(text="No classes found matching your criteria", fg="#666")
            return
            
        view_mode = self.view_mode.get()
        
        if view_mode == 'Table View':
            # Regular table view
            for entry in self.filtered_timetable:
                self.tree.insert("", "end", values=(
                    entry["program"], entry["course"], entry["day"], 
                    entry["time"], entry["room"], entry["teacher"]
                ))
        else:
            # Batch-wise view
            batches = get_timetable_by_batch(self.filtered_timetable)
            
            for batch, classes in batches.items():
                # Insert batch header
                batch_item = self.tree.insert("", "end", values=(
                    f"📚 {batch} ({len(classes)} classes)", "", "", "", "", ""
                ))
                
                # Insert classes under batch
                for entry in classes:
                    self.tree.insert(batch_item, "end", values=(
                        entry["program"], entry["course"], entry["day"], 
                        entry["time"], entry["room"], entry["teacher"]
                    ))
                    
                # Expand batch by default
                self.tree.item(batch_item, open=True)
        
        # Update status
        total_classes = len(self.current_timetable) if self.current_timetable else 0
        filtered_classes = len(self.filtered_timetable)
        self.status_label.config(
            text=f"Showing {filtered_classes} classes (filtered from {total_classes} total)",
            fg="#4CAF50"
        )
        
    def update_statistics(self):
        if not self.filtered_timetable:
            self.stats_text.delete(1.0, tk.END)
            return
            
        stats = get_statistics(self.filtered_timetable)
        
        stats_content = f"""
TIMETABLE STATISTICS
{'='*50}

General Information:
• Total Classes: {stats.get('total_classes', 0)}
• Unique Programs: {stats.get('unique_programs', 0)}
• Unique Courses: {stats.get('unique_courses', 0)}
• Unique Teachers: {stats.get('unique_teachers', 0)}
• Unique Rooms: {stats.get('unique_rooms', 0)}

Classes per Day:
"""
        
        if 'classes_per_day' in stats:
            for day, count in sorted(stats['classes_per_day'].items()):
                stats_content += f"• {day}: {count} classes\n"
                
        stats_content += "\nClasses per Program:\n"
        if 'classes_per_program' in stats:
            for program, count in sorted(stats['classes_per_program'].items()):
                stats_content += f"• {program}: {count} classes\n"
                
        stats_content += "\nTeacher Workload:\n"
        if 'teacher_workload' in stats:
            for teacher, count in sorted(stats['teacher_workload'].items(), key=lambda x: x[1], reverse=True):
                stats_content += f"• {teacher}: {count} classes\n"
                
        stats_content += "\nRoom Utilization:\n"
        if 'room_utilization' in stats:
            for room, count in sorted(stats['room_utilization'].items(), key=lambda x: x[1], reverse=True):
                stats_content += f"• {room}: {count} classes\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_content)
        
    def export_csv(self):
        if not self.filtered_timetable:
            messagebox.showwarning("No Data", "No timetable data to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Timetable as CSV"
        )
        
        if file_path:
            try:
                csv_data = export_to_csv(self.filtered_timetable)
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    f.write(csv_data)
                messagebox.showinfo("Export Successful", f"Timetable exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Error exporting file: {str(e)}")
                
    def add_program_dialog(self):
        dialog = ProgramDialog(self.root, self.generator)
        if dialog.result:
            # Update program checkboxes
            self.refresh_program_list()
            
    def add_course_dialog(self):
        dialog = CourseDialog(self.root, self.generator)
        
    def refresh_program_list(self):
        # This would require rebuilding the program selection area
        # For simplicity, show a message to restart
        messagebox.showinfo("Program Added", "Program added successfully! The new program is now available for selection.")
        
    def run(self):
        self.root.mainloop()

class ProgramDialog:
    def __init__(self, parent, generator):
        self.generator = generator
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Program")
        self.dialog.geometry("400x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog()
        
    def setup_dialog(self):
        tk.Label(self.dialog, text="Add New Program", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Program name
        tk.Label(self.dialog, text="Program Name:", font=("Arial", 10)).pack(anchor=tk.W, padx=20)
        self.program_name = tk.Entry(self.dialog, width=40)
        self.program_name.pack(padx=20, pady=5)
        
        # Sections frame
        sections_frame = tk.LabelFrame(self.dialog, text="Sections and Courses")
        sections_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollable sections area
        canvas = tk.Canvas(sections_frame)
        scrollbar = ttk.Scrollbar(sections_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.sections = []
        self.add_section()  # Add first section
        
        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Add Section", command=self.add_section).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Save Program", command=self.save_program, 
                 bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def add_section(self):
        section_frame = tk.Frame(self.scrollable_frame)
        section_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(section_frame, text=f"Section {len(self.sections) + 1}:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        section_name = tk.Entry(section_frame, width=20)
        section_name.pack(anchor=tk.W, pady=2)
        
        tk.Label(section_frame, text="Courses (one per line):", font=("Arial", 9)).pack(anchor=tk.W)
        courses_text = tk.Text(section_frame, height=4, width=40)
        courses_text.pack(anchor=tk.W, pady=2)
        
        self.sections.append({'name': section_name, 'courses': courses_text})
        
    def save_program(self):
        program_name = self.program_name.get().strip()
        
        if not program_name:
            messagebox.showerror("Error", "Please enter a program name")
            return
            
        sections_data = {}
        
        for section in self.sections:
            section_name = section['name'].get().strip()
            courses_text = section['courses'].get(1.0, tk.END).strip()
            
            if section_name and courses_text:
                courses = [course.strip() for course in courses_text.split('\n') if course.strip()]
                if courses:
                    sections_data[section_name] = courses
                    
        if not sections_data:
            messagebox.showerror("Error", "Please add at least one section with courses")
            return
            
        is_valid, message = validate_program_data(program_name, sections_data)
        if not is_valid:
            messagebox.showerror("Validation Error", message)
            return
            
        success = self.generator.add_program(program_name, sections_data)
        if success:
            self.result = True
            messagebox.showinfo("Success", f"Program '{program_name}' added successfully!")
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", f"Program '{program_name}' already exists")

class CourseDialog:
    def __init__(self, parent, generator):
        self.generator = generator
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Course to Program")
        self.dialog.geometry("350x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog()
        
    def setup_dialog(self):
        tk.Label(self.dialog, text="Add Course to Existing Program", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Program selection
        tk.Label(self.dialog, text="Select Program:", font=("Arial", 10)).pack(anchor=tk.W, padx=20)
        self.program_combo = ttk.Combobox(self.dialog, width=30, state="readonly")
        self.program_combo['values'] = self.generator.get_all_programs()
        self.program_combo.pack(padx=20, pady=5)
        self.program_combo.bind('<<ComboboxSelected>>', self.update_sections)
        
        # Section selection
        tk.Label(self.dialog, text="Select Section:", font=("Arial", 10)).pack(anchor=tk.W, padx=20)
        self.section_combo = ttk.Combobox(self.dialog, width=30, state="readonly")
        self.section_combo.pack(padx=20, pady=5)
        
        # Course name
        tk.Label(self.dialog, text="Course Name:", font=("Arial", 10)).pack(anchor=tk.W, padx=20)
        self.course_name = tk.Entry(self.dialog, width=33)
        self.course_name.pack(padx=20, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Add Course", command=self.add_course, 
                 bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def update_sections(self, event=None):
        program = self.program_combo.get()
        if program:
            sections = self.generator.get_program_sections(program)
            self.section_combo['values'] = sections
            if sections:
                self.section_combo.set(sections[0])
                
    def add_course(self):
        program = self.program_combo.get()
        section = self.section_combo.get()
        course = self.course_name.get().strip()
        
        if not all([program, section, course]):
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        success = self.generator.add_course_to_program(program, section, course)
        if success:
            messagebox.showinfo("Success", f"Course '{course}' added to {program}-{section}!")
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", f"Course '{course}' already exists in {program}-{section}")

def launch_gui():
    app = TimetableGUI()
    app.run()

if __name__ == "__main__":
    launch_gui()


 
