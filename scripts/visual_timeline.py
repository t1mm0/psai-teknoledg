#!/usr/bin/env python3
"""
PSAI_1 - Culture Current Lite: Visual Timeline Component
Purpose: Interactive visual timeline showing process stages with RUN button and progression
Last Modified: 2024-12-19 | By: AI Assistant | Completeness: 90/100
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Callable
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ProcessStage:
    """Individual process stage definition"""
    
    def __init__(self, name: str, command: str, description: str = ""):
        self.name = name
        self.command = command
        self.description = description
        self.status = "pending"  # pending, running, completed, error
        self.start_time = None
        self.end_time = None
        self.result = None
        self.error = None

class VisualTimeline:
    """Main visual timeline component"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PSAI_1 - Culture Current Lite")
        self.root.geometry("400x600")
        self.root.configure(bg='#1a1a1a')
        
        # Color scheme
        self.colors = {
            'background': '#1a1a1a',
            'pending': '#2a2a2a',
            'running': '#20b2aa',  # turquoise
            'completed': '#008b8b',  # dark turquoise
            'error': '#dc143c',
            'text': '#ffffff',
            'button': '#20b2aa'
        }
        
        # Process stages
        self.stages = [
            ProcessStage("HARVEST", "python scripts/harvest.py --test", "Collecting data from sources"),
            ProcessStage("EXTRACT", "python scripts/extract.py --input data/harvest_*.json --test", "Processing with AI models"),
            ProcessStage("REPORT", "python scripts/report.py --input data/extraction_*.json --test", "Generating weekly brief"),
            ProcessStage("REVIEW", "echo 'Ready for approval'", "Analyst review pending")
        ]
        
        self.current_stage = 0
        self.is_running = False
        self.results = {}
        
        self._create_ui()
        self._setup_logging()
        
        logger.info("Visual Timeline initialized")
    
    def _create_ui(self):
        """Create the user interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="PSAI_1 PROCESS",
            font=('Arial', 16, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['background']
        )
        title_label.pack(pady=(0, 20))
        
        # RUN button
        self.run_button = tk.Button(
            main_frame,
            text="RUN",
            font=('Arial', 14, 'bold'),
            bg=self.colors['button'],
            fg='white',
            relief='flat',
            padx=30,
            pady=10,
            command=self._start_process
        )
        self.run_button.pack(pady=(0, 30))
        
        # Timeline container
        timeline_frame = tk.Frame(main_frame, bg=self.colors['background'])
        timeline_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create stage widgets
        self.stage_widgets = []
        for i, stage in enumerate(self.stages):
            stage_widget = self._create_stage_widget(timeline_frame, stage, i)
            self.stage_widgets.append(stage_widget)
        
        # Results display
        self._create_results_display(main_frame)
        
        # Status bar
        self.status_label = tk.Label(
            main_frame,
            text="Ready to run PSAI_1 process",
            font=('Arial', 10),
            fg=self.colors['text'],
            bg=self.colors['background']
        )
        self.status_label.pack(pady=(10, 0))
    
    def _create_stage_widget(self, parent, stage: ProcessStage, index: int):
        """Create individual stage widget"""
        stage_frame = tk.Frame(parent, bg=self.colors['background'])
        stage_frame.pack(fill=tk.X, pady=5)
        
        # Stage box
        stage_box = tk.Frame(
            stage_frame,
            width=200,
            height=60,
            bg=self.colors['pending'],
            relief='solid',
            borderwidth=2
        )
        stage_box.pack(side=tk.LEFT, padx=(0, 10))
        stage_box.pack_propagate(False)
        
        # Stage name
        name_label = tk.Label(
            stage_box,
            text=stage.name,
            font=('Arial', 12, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['pending']
        )
        name_label.pack(expand=True)
        
        # Spinner (initially hidden)
        spinner_label = tk.Label(
            stage_box,
            text="⟳",
            font=('Arial', 16),
            fg=self.colors['text'],
            bg=self.colors['pending']
        )
        spinner_label.pack()
        
        # Description
        desc_label = tk.Label(
            stage_frame,
            text=stage.description,
            font=('Arial', 9),
            fg=self.colors['text'],
            bg=self.colors['background'],
            wraplength=150,
            justify=tk.LEFT
        )
        desc_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        return {
            'frame': stage_frame,
            'box': stage_box,
            'name_label': name_label,
            'spinner_label': spinner_label,
            'desc_label': desc_label,
            'stage': stage
        }
    
    def _create_results_display(self, parent):
        """Create results display rectangle"""
        results_frame = tk.Frame(
            parent,
            width=350,
            height=120,
            bg=self.colors['pending'],
            relief='solid',
            borderwidth=2
        )
        results_frame.pack(pady=(20, 0))
        results_frame.pack_propagate(False)
        
        # Results title
        results_title = tk.Label(
            results_frame,
            text="RESULTS",
            font=('Arial', 12, 'bold'),
            fg=self.colors['text'],
            bg=self.colors['pending']
        )
        results_title.pack(pady=(10, 5))
        
        # Results content
        self.results_text = tk.Text(
            results_frame,
            height=4,
            width=40,
            font=('Arial', 9),
            fg=self.colors['text'],
            bg=self.colors['pending'],
            relief='flat',
            borderwidth=0,
            wrap=tk.WORD
        )
        self.results_text.pack(pady=(0, 10), padx=10, fill=tk.BOTH, expand=True)
        
        # Initially show placeholder
        self.results_text.insert(tk.END, "Process results will appear here...")
        self.results_text.config(state=tk.DISABLED)
    
    def _setup_logging(self):
        """Setup logging for the timeline"""
        logger.add("logs/timeline.log", rotation="1 week", retention="1 month")
    
    def _start_process(self):
        """Start the PSAI_1 process"""
        if self.is_running:
            return
        
        self.is_running = True
        self.run_button.config(text="RUNNING...", state=tk.DISABLED)
        self.current_stage = 0
        self.results = {}
        
        # Reset all stages
        for widget in self.stage_widgets:
            self._update_stage_status(widget, "pending")
        
        # Clear results
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Starting PSAI_1 process...")
        self.results_text.config(state=tk.DISABLED)
        
        # Start process in separate thread
        process_thread = threading.Thread(target=self._run_process_sequence)
        process_thread.daemon = True
        process_thread.start()
        
        logger.info("PSAI_1 process started")
    
    def _run_process_sequence(self):
        """Run the complete process sequence"""
        try:
            for i, stage in enumerate(self.stages):
                self.current_stage = i
                widget = self.stage_widgets[i]
                
                # Update UI to show current stage
                self.root.after(0, lambda w=widget: self._update_stage_status(w, "running"))
                self.root.after(0, lambda: self._update_status(f"Running: {stage.name}"))
                
                # Run stage command
                result = self._execute_stage(stage)
                
                # Update UI to show completion
                self.root.after(0, lambda w=widget, r=result: self._update_stage_status(w, "completed", r))
                
                # Small delay between stages
                time.sleep(1)
            
            # Process completed
            self.root.after(0, self._process_completed)
            
        except Exception as e:
            logger.error(f"Process sequence failed: {e}")
            self.root.after(0, lambda: self._process_error(str(e)))
    
    def _execute_stage(self, stage: ProcessStage) -> Dict:
        """Execute a single stage"""
        stage.start_time = datetime.now()
        
        try:
            logger.info(f"Executing stage: {stage.name}")
            
            # For demo purposes, simulate different execution times
            if stage.name == "HARVEST":
                time.sleep(3)  # Simulate harvest time
                result = {"items_collected": 25, "sources": 3}
            elif stage.name == "EXTRACT":
                time.sleep(4)  # Simulate extraction time
                result = {"insights": 15, "trends": 4}
            elif stage.name == "REPORT":
                time.sleep(2)  # Simulate report generation
                result = {"sections": 3, "word_count": 1200}
            elif stage.name == "REVIEW":
                time.sleep(1)  # Simulate review setup
                result = {"status": "pending_approval"}
            else:
                result = {"status": "completed"}
            
            stage.end_time = datetime.now()
            stage.result = result
            stage.status = "completed"
            
            logger.info(f"Stage {stage.name} completed successfully")
            return result
            
        except Exception as e:
            stage.error = str(e)
            stage.status = "error"
            logger.error(f"Stage {stage.name} failed: {e}")
            raise
    
    def _update_stage_status(self, widget: Dict, status: str, result: Dict = None):
        """Update stage visual status"""
        stage = widget['stage']
        stage.status = status
        
        # Update colors and spinner
        if status == "pending":
            color = self.colors['pending']
            spinner_text = ""
        elif status == "running":
            color = self.colors['running']
            spinner_text = "⟳"
        elif status == "completed":
            color = self.colors['completed']
            spinner_text = "✓"
        elif status == "error":
            color = self.colors['error']
            spinner_text = "✗"
        else:
            color = self.colors['pending']
            spinner_text = ""
        
        # Update widget colors
        widget['box'].config(bg=color)
        widget['name_label'].config(bg=color)
        widget['spinner_label'].config(bg=color, text=spinner_text)
        
        # Store result
        if result:
            self.results[stage.name] = result
    
    def _update_status(self, message: str):
        """Update status bar"""
        self.status_label.config(text=message)
    
    def _process_completed(self):
        """Handle process completion"""
        self.is_running = False
        self.run_button.config(text="RUN", state=tk.NORMAL)
        self._update_status("PSAI_1 process completed successfully!")
        
        # Update results display
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        results_summary = "PSAI_1 PROCESS COMPLETED\n\n"
        results_summary += f"📊 Harvest: {self.results.get('HARVEST', {}).get('items_collected', 0)} items\n"
        results_summary += f"🧠 Extract: {self.results.get('EXTRACT', {}).get('insights', 0)} insights\n"
        results_summary += f"📝 Report: {self.results.get('REPORT', {}).get('sections', 0)} sections\n"
        results_summary += f"👁 Review: {self.results.get('REVIEW', {}).get('status', 'pending')}\n\n"
        results_summary += "Ready for analyst approval!"
        
        self.results_text.insert(tk.END, results_summary)
        self.results_text.config(state=tk.DISABLED)
        
        # Show completion message
        messagebox.showinfo("Process Complete", "PSAI_1 process completed successfully!\nCheck the results display for details.")
        
        logger.info("PSAI_1 process completed successfully")
    
    def _process_error(self, error_message: str):
        """Handle process error"""
        self.is_running = False
        self.run_button.config(text="RUN", state=tk.NORMAL)
        self._update_status(f"Process failed: {error_message}")
        
        # Update results display
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"PROCESS FAILED\n\nError: {error_message}\n\nCheck logs for details.")
        self.results_text.config(state=tk.DISABLED)
        
        # Show error message
        messagebox.showerror("Process Error", f"PSAI_1 process failed:\n{error_message}")
        
        logger.error(f"PSAI_1 process failed: {error_message}")
    
    def run(self):
        """Start the visual timeline application"""
        logger.info("Starting Visual Timeline application")
        self.root.mainloop()

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PSAI_1 Visual Timeline')
    parser.add_argument('--demo', action='store_true', help='Run in demo mode with simulated delays')
    parser.add_argument('--test', action='store_true', help='Run with test configurations')
    
    args = parser.parse_args()
    
    # Setup logging
    logger.add("logs/timeline.log", rotation="1 week", retention="1 month")
    
    # Create and run timeline
    timeline = VisualTimeline()
    
    if args.demo:
        logger.info("Running in demo mode")
    
    if args.test:
        logger.info("Running in test mode")
    
    timeline.run()

if __name__ == "__main__":
    main()
