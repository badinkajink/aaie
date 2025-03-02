import multiprocessing
import subprocess

# Define ranges for chunks
# chunks = [(0, 60), (60, 120), (120, 180), (180, 240)]
# generate 24 chunks of 10
chunks = [(i*40, (i+1)*40) for i in range(6)]
fp = 'conversations/gpt-4o-mini/run_2'
def run_chunk(start, end):
    subprocess.run(["python", "run_structured_interaction.py", str(start), str(end), fp])

# Run in parallel
if __name__ == "__main__":
    processes = []
    for start, end in chunks:
        p = multiprocessing.Process(target=run_chunk, args=(start, end))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()  # Wait for all processes to finish
