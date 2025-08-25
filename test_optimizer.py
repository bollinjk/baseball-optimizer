import baseball_optimizer as bo
import random

def test_player_manager():
    print("Testing Player Manager...")
    manager = bo.PlayerManager(bo.playerDictionary)
    manager.display_roster()
    print("\nPlayer Manager test complete!")

def test_simulator():
    print("\nTesting Baseball Simulator...")
    manager = bo.PlayerManager(bo.playerDictionary)
    simulator = bo.BaseballSimulator(manager.players)
    
    # Test single game
    lineup = list(manager.players.keys())
    result = simulator.simulate_game(lineup)
    print(f"Test game runs scored: {result['runs']}")
    print("Baseball Simulator test complete!")

def test_quick_optimization():
    print("\nTesting Quick Optimization...")
    manager = bo.PlayerManager(bo.playerDictionary)
    optimizer = bo.LineupOptimizer(manager.players, mode='quick')
    
    # Run a small number of simulations for testing
    player_names = list(manager.players.keys())
    best_lineups = []
    
    print("\nTesting 5 random lineups with 10 games each...")
    for i in range(5):
        lineup = list(random.sample(player_names, len(player_names)))
        total_runs = 0
        
        for _ in range(10):  # 10 games per lineup
            result = optimizer.simulator.simulate_game(lineup)
            total_runs += result['runs']
        
        avg_runs = total_runs / 10
        best_lineups.append((lineup, avg_runs))
        print(f"Lineup {i+1} average runs: {avg_runs:.2f}")
    
    best_lineups.sort(key=lambda x: x[1], reverse=True)
    
    print("\nTop 3 lineups from test sample:")
    for i, (lineup, avg_runs) in enumerate(best_lineups[:3], 1):
        print(f"{i}. Average Runs: {avg_runs:.2f}")
        print(f"   Lineup: {' -> '.join(lineup)}")
    
    print("Quick Optimization test complete!")

if __name__ == "__main__":
    print("Starting tests...\n")
    test_player_manager()
    test_simulator()
    test_quick_optimization()
    print("\nAll tests complete!")
