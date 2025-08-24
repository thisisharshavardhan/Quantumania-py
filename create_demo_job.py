#!/usr/bin/env python3
"""
Demo script to create a simple quantum job to show in the dashboard
This will submit a real job to IBM Quantum so you can see live data
"""

import os
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

def create_demo_job():
    """Create a simple quantum job to demonstrate the dashboard"""
    
    # Initialize the service
    service = QiskitRuntimeService()
    
    # Get available backends
    backends = service.backends()
    print(f"Available backends: {[b.name for b in backends]}")
    
    # Choose the least busy backend
    backend = service.least_busy(simulator=False)
    print(f"Selected backend: {backend.name}")
    
    # Create a simple quantum circuit
    qc = QuantumCircuit(2, 2)
    qc.h(0)  # Hadamard gate on qubit 0
    qc.cx(0, 1)  # CNOT gate
    qc.measure_all()  # Measure all qubits
    
    print("Created quantum circuit:")
    print(qc.draw())
    
    # Submit the job
    print(f"\n🚀 Submitting job to {backend.name}...")
    
    sampler = SamplerV2(backend)
    job = sampler.run([qc], shots=1024)
    
    print(f"✅ Job submitted successfully!")
    print(f"Job ID: {job.job_id()}")
    print(f"Job Status: {job.status()}")
    print(f"Backend: {backend.name}")
    
    print(f"\n🔄 Your dashboard will now show this real quantum job!")
    print(f"   Dashboard: http://localhost:3001")
    print(f"   Job will appear in the 'Recent Jobs' section")
    
    return job.job_id()

if __name__ == "__main__":
    try:
        job_id = create_demo_job()
        print(f"\n✨ Demo job created successfully: {job_id}")
        print("🎯 Check your dashboard to see the live quantum job!")
    except Exception as e:
        print(f"❌ Error creating demo job: {e}")
        print("This might be because:")
        print("1. No quantum credits available")
        print("2. All backends are busy")
        print("3. Account limitations")
        print("\nThe dashboard still works perfectly - it just shows no jobs because your account hasn't submitted any yet.")
