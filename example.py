import meta_loop

best_agent = meta_loop.build_agent(
    instruction="Create a calculator agent that always wrong.",
    probe_count=16,
)
