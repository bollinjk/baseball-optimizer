# Import required libraries
import random
import math
import statistics
import itertools
from concurrent.futures import ThreadPoolExecutor
import threading
import time
from typing import Dict, List, Tuple
import pickle
import os
import sys
import queue
import uuid
import signal
import win32api

def handler(sig, frame):
    if sig == signal.SIGINT:
        print("\nCtrl+C detected. Gracefully shutting down...")
        win32api.GenerateConsoleCtrlEvent(signal.CTRL_C_EVENT, 0)

# Set up signal handlers
signal.signal(signal.SIGINT, handler)

class KeyboardMonitor:
    def __init__(self, stop_word="bova"):
        self.running = True
        self.stop_word = stop_word.lower()
        self.input_queue = queue.Queue()
        self.thread = threading.Thread(target=self._input_monitor)
        self.thread.daemon = True
        self.stop_event = threading.Event()
        self.input_buffer = ""
    
    def start(self):
        print(f"\nTo stop optimization:")
        print(f"- Type '{self.stop_word}' and press Enter")
        print("- Or press Ctrl+C")
        print("- Or close the terminal")
        self.thread.start()
    
    def stop(self):
        self.running = False
        self.stop_event.set()
        # Add empty input to unblock the input call
        if self.thread.is_alive():
            self.input_queue.put("")
    
    def _input_monitor(self):
        import sys
        import msvcrt
        
        while self.running:
            try:
                # Check for input without blocking
                if msvcrt.kbhit():
                    # Read input character by character
                    char = msvcrt.getwch()
                    if char == '\r':  # Enter key
                        print()  # Move to next line
                        if self.input_buffer.lower() == self.stop_word:
                            print("\nStop command received. Gracefully shutting down...")
                            self.running = False
                            self.stop_event.set()
                        self.input_buffer = ""
                    else:
                        print(char, end='', flush=True)  # Echo character
                        self.input_buffer += char
                
                # Check if we should exit
                if self.stop_event.is_set():
                    break
                    
                # Small sleep to prevent CPU spinning
                time.sleep(0.1)
                    
            except (EOFError, KeyboardInterrupt):
                self.running = False
                self.stop_event.set()
                break
    
    def should_continue(self):
        return self.running and not self.stop_event.is_set()

class Player:
    def __init__(self, name: str, hit_chance: float, hit_probabilities: List[float], current_base: int = 0, is_batting: bool = False):
        self.name = name
        self.hit_chance = hit_chance
        self.hit_probabilities = hit_probabilities  # [single, double, triple, HR]
        self.current_base = current_base
        self.is_batting = is_batting
        
    def __str__(self):
        return f"{self.name}: {self.hit_chance*100:.1f}% hit chance"

class PlayerManager:
    def __init__(self, player_dictionary: Dict):
        self.players = {}
        # Convert dictionary format to Player objects
        for name, stats in player_dictionary.items():
            if name != "Kai" or name not in self.players:  # Skip duplicate Kai
                self.players[name] = Player(
                    name=name,
                    hit_chance=stats[1],
                    hit_probabilities=stats[2],
                    current_base=stats[3],
                    is_batting=(stats[0] == 1)
                )
    
    def display_roster(self):
        print("\nCurrent Roster:")
        print("=" * 70)
        print(f"{'Name':<15} {'Hit Chance':<12} {'Single%':<10} {'Double%':<10} {'Triple%':<10} {'HR%':<10}")
        print("-" * 70)
        for name, player in self.players.items():
            print(f"{name:<15} {player.hit_chance:<12.3f} {player.hit_probabilities[0]:<10.3f} "
                  f"{player.hit_probabilities[1]:<10.3f} {player.hit_probabilities[2]:<10.3f} "
                  f"{player.hit_probabilities[3]:<10.3f}")
    
    def update_players(self):
        while True:
            self.display_roster()
            print("\nWould you like to update any player stats?")
            print("1. Yes")
            print("2. No - Continue to simulation")
            choice = input("Enter choice (1-2): ")
            
            if choice == "2":
                break
            elif choice == "1":
                self.update_player_stats()
    
    def update_player_stats(self):
        print("\nSelect player to update:")
        players = list(self.players.keys())
        for i, name in enumerate(players, 1):
            print(f"{i}. {name}")
        
        try:
            player_choice = int(input(f"Enter player number (1-{len(players)}): "))
            if player_choice < 1 or player_choice > len(players):
                print("Invalid player number")
                return
            
            player_name = players[player_choice-1]
            player = self.players[player_name]
            
            print("\nSelect what to update:")
            print("1. Hit Chance")
            print("2. Hit Probabilities (Single, Double, Triple, HR)")
            
            stat_choice = int(input("Enter choice (1-2): "))
            if stat_choice < 1 or stat_choice > 2:
                print("Invalid choice")
                return
            
            if stat_choice == 1:
                new_value = float(input("Enter new hit chance (as decimal, e.g. 0.300): "))
                if new_value < 0 or new_value > 1:
                    print("Value must be between 0 and 1")
                    return
                player.hit_chance = new_value
            else:
                print("\nEnter new hit probabilities (as decimals):")
                print("Current values:")
                print(f"Singles: {player.hit_probabilities[0]:.3f}")
                print(f"Doubles: {player.hit_probabilities[1]:.3f}")
                print(f"Triples: {player.hit_probabilities[2]:.3f}")
                print(f"Home Runs: {player.hit_probabilities[3]:.3f}")
                print("\nEnter new values:")
                
                while True:
                    try:
                        singles = float(input("Singles probability: "))
                        doubles = float(input("Doubles probability: "))
                        triples = float(input("Triples probability: "))
                        homers = float(input("Home Runs probability: "))
                        
                        # Validate each value is between 0 and 1
                        valid = True
                        for val, name in [(singles, "Singles"), (doubles, "Doubles"), 
                                        (triples, "Triples"), (homers, "Home Runs")]:
                            if val < 0 or val > 1:
                                print(f"{name} probability must be between 0 and 1")
                                valid = False
                                break
                        
                        if not valid:
                            print("\nPlease enter all probabilities again.")
                            continue
                        
                        # Calculate total and check if sum is 1
                        total = singles + doubles + triples + homers
                        if abs(total - 1.0) > 0.001:
                            print(f"\nError: Hit probabilities sum to {total:.3f}")
                            print("They must sum to 1.0. Please enter all probabilities again.")
                            continue
                        
                        # If we get here, all values are valid
                        player.hit_probabilities = [singles, doubles, triples, homers]
                        print("\nHit probabilities updated successfully!")
                        break
                        
                    except ValueError:
                        print("Invalid input. Please enter decimal numbers.")
                        continue
                    
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

class BaseballSimulator:
    def __init__(self, players: Dict[str, Player]):
        self.players = players
        self.metrics = MetricsTracker()
        
    def simulate_game(self, lineup: List[str]) -> Dict:
        game_players = {name: Player(
            name=self.players[name].name,
            hit_chance=self.players[name].hit_chance,
            hit_probabilities=self.players[name].hit_probabilities.copy(),
            current_base=0,
            is_batting=False
        ) for name in lineup}
        
        game_players[lineup[0]].is_batting = True
        sumRuns = 0
        inning_stats = []
        
        for inning in range(1, 7):
            currentOuts = 0
            inningRuns = 0
            
            while currentOuts < 3 and inningRuns < 5:
                current_batter = next(player for player in game_players.values() if player.is_batting)
                
                if random.random() < current_batter.hit_chance:
                    typeOfHit = random.random()
                    cumulative_prob = 0
                    
                    for base in range(4):
                        cumulative_prob += current_batter.hit_probabilities[base]
                        if typeOfHit < cumulative_prob:
                            current_batter.current_base = base + 1
                            break
                    
                    # Handle home run
                    if current_batter.current_base == 4:
                        inningRuns += 1
                        sumRuns += 1
                        current_batter.current_base = 0
                    
                    # Advance runners
                    for runner in game_players.values():
                        if runner.current_base > 0 and runner != current_batter:
                            runner.current_base += current_batter.current_base
                            if runner.current_base >= 4:
                                inningRuns += 1
                                sumRuns += 1
                                runner.current_base = 0
                                if inningRuns >= 5:
                                    break
                    
                    if inningRuns >= 5:
                        break
                else:
                    currentOuts += 1
                
                # Update batting order
                current_idx = lineup.index(current_batter.name)
                next_idx = (current_idx + 1) % len(lineup)
                current_batter.is_batting = False
                game_players[lineup[next_idx]].is_batting = True
            
            # Reset bases after inning
            for player in game_players.values():
                player.current_base = 0
            
            inning_stats.append({
                'runs': inningRuns,
                'five_run_inning': inningRuns == 5
            })
        
        game_result = {
            'runs': sumRuns,
            'inning_stats': inning_stats
        }
        
        self.metrics.update_game_metrics(game_result)
        return game_result

class MetricsTracker:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.runs_by_inning = [[] for _ in range(6)]
        self.five_run_innings = 0
        self.total_runs = 0
        self.games_played = 0
    
    def update_game_metrics(self, game_result):
        self.total_runs += game_result['runs']
        self.games_played += 1
        
        for i, inning in enumerate(game_result['inning_stats']):
            self.runs_by_inning[i].append(inning['runs'])
            if inning['five_run_inning']:
                self.five_run_innings += 1
    
    def get_game_metrics(self):
        if self.games_played == 0:
            return None
            
        return {
            'avg_runs': self.total_runs / self.games_played,
            'five_run_innings': self.five_run_innings,
            'five_run_inning_pct': self.five_run_innings / (self.games_played * 6),
            'runs_by_inning': [
                {
                    'avg': sum(runs) / len(runs) if runs else 0,
                    'max': max(runs) if runs else 0,
                    'zero_run_pct': runs.count(0) / len(runs) if runs else 0
                }
                for runs in self.runs_by_inning
            ]
        }

class LineupOptimizer:
    def __init__(self, players: Dict[str, Player], mode='quick', progress_callback=None):
        self.players = players
        self.mode = mode
        self.simulator = BaseballSimulator(players)
        self.best_lineups = []
        self.progress = 0.0
        self.running = True
        self.progress_callback = progress_callback
    
    def optimize(self):
        if self.mode == 'quick':
            return self.quick_optimize()
        else:
            return self.deep_optimize()
    
    def quick_optimize(self):
        games_per_lineup = 10
        sample_size = min(100000, math.factorial(len(self.players)))
        player_names = list(self.players.keys())
        
        best_lineups = []
        total_evaluated = 0
        
        for _ in range(sample_size):
            if not self.running:
                print("\nQuick optimization interrupted...")
                break
                
            lineup = list(random.sample(player_names, len(player_names)))
            total_runs = 0
            
            for _ in range(games_per_lineup):
                result = self.simulator.simulate_game(lineup)
                total_runs += result['runs']
            
            avg_runs = total_runs / games_per_lineup
            best_lineups.append((lineup, avg_runs))
            
            total_evaluated += 1
            self.progress = (total_evaluated / sample_size) * 100
            if self.progress_callback:
                self.progress_callback(self.progress)
        
        best_lineups.sort(key=lambda x: x[1], reverse=True)
        return best_lineups[:3]
    
    def deep_optimize(self):
        games_per_lineup = 100
        player_names = list(self.players.keys())
        all_lineups = list(itertools.permutations(player_names))
        total_lineups = len(all_lineups)
        
        best_lineups = []
        total_evaluated = 0
        
        try:
            for lineup in all_lineups:
                if not self.running:
                    print("\nOptimization interrupted...")
                    break
                    
                lineup = list(lineup)
                total_runs = 0
                
                for _ in range(games_per_lineup):
                    result = self.simulator.simulate_game(lineup)
                    total_runs += result['runs']
                
                avg_runs = total_runs / games_per_lineup
                best_lineups.append((lineup, avg_runs))
                
                total_evaluated += 1
                self.progress = (total_evaluated / total_lineups) * 100
                if self.progress_callback:
                    self.progress_callback(self.progress)
                    
        except Exception as e:
            print(f"\nError during optimization: {str(e)}")
        
        finally:
            # Sort and return best lineups
            best_lineups.sort(key=lambda x: x[1], reverse=True)
            return best_lineups[:3]
    

class ParallelOptimizer:
    def __init__(self, players: Dict[str, Player]):
        self.players = players
        self.quick_results = None
        self.deep_results = None
        self.progress = {'quick': 0.0, 'deep': 0.0}
        self.lock = threading.Lock()
        self.running = True
        self.quick_results_displayed = False
        self.deep_results_displayed = False
        self.keyboard_monitor = KeyboardMonitor()
    
    def run_parallel_analysis(self):
        # Reset progress tracking
        self.progress = {'quick': 0.0, 'deep': 0.0}
        self.quick_results_displayed = False
        self.deep_results_displayed = False
        
        # Start keyboard monitor
        self.keyboard_monitor.start()
        
        try:
            with ThreadPoolExecutor() as executor:
                quick_future = executor.submit(self.run_quick_analysis)
                deep_future = executor.submit(self.run_deep_analysis)
                
                # Start progress monitoring
                progress_thread = threading.Thread(target=self.monitor_progress)
                progress_thread.daemon = True
                progress_thread.start()
                
                # Monitor for stop signal
                try:
                    while True:
                        if not self.keyboard_monitor.should_continue():
                            print("\nStopping optimization...")
                            self.running = False
                            win32api.GenerateConsoleCtrlEvent(signal.CTRL_C_EVENT, 0)
                            break
                        
                        if quick_future.done() and deep_future.done():
                            break
                            
                        time.sleep(0.1)
                except (KeyboardInterrupt, SystemExit):
                    print("\nInterrupt received. Stopping optimization...")
                    self.running = False
                    self.keyboard_monitor.stop()
                    win32api.GenerateConsoleCtrlEvent(signal.CTRL_C_EVENT, 0)
                
                return quick_future, deep_future
                
        except KeyboardInterrupt:
            print("\nKeyboard interrupt detected. Stopping optimization...")
            self.running = False
            self.keyboard_monitor.stop()
            raise
    
    def run_quick_analysis(self):
        def update_quick_progress(progress):
            with self.lock:
                self.progress['quick'] = progress
        
        optimizer = LineupOptimizer(self.players, mode='quick', progress_callback=update_quick_progress)
        
        def check_stop():
            if not self.running or not self.keyboard_monitor.should_continue():
                optimizer.running = False
        
        # Start stop signal monitor
        stop_monitor = threading.Thread(target=lambda: [check_stop() or time.sleep(0.1) for _ in iter(bool, True)])
        stop_monitor.daemon = True
        stop_monitor.start()
        
        self.quick_results = optimizer.optimize()
        with self.lock:
            self.progress['quick'] = 100.0
        return self.quick_results
    
    def run_deep_analysis(self):
        def update_deep_progress(progress):
            with self.lock:
                self.progress['deep'] = progress
        
        optimizer = LineupOptimizer(self.players, mode='deep', progress_callback=update_deep_progress)
        
        def check_stop():
            if not self.running or not self.keyboard_monitor.should_continue():
                optimizer.running = False
        
        # Start stop signal monitor
        stop_monitor = threading.Thread(target=lambda: [check_stop() or time.sleep(0.1) for _ in iter(bool, True)])
        stop_monitor.daemon = True
        stop_monitor.start()
        
        try:
            self.deep_results = optimizer.optimize()
            with self.lock:
                self.progress['deep'] = 100.0
            return self.deep_results
        except KeyboardInterrupt:
            print("\nInterrupting deep analysis...")
            optimizer.running = False
            return None
    
    def monitor_progress(self):
        while self.running and self.keyboard_monitor.should_continue():
            try:
                self.display_progress()
                
                if self.progress['quick'] >= 100 and self.progress['deep'] >= 100:
                    break
                    
                time.sleep(0.05)  # Update display every 50ms for smooth progress bar
                
            except Exception as e:
                print(f"\nProgress monitoring error: {str(e)}")
                time.sleep(1)
        
        # Final progress display
        self.display_progress()
    
    def display_progress(self):
        # Only display results if we have them and haven't shown them yet
        if self.quick_results and not self.quick_results_displayed:
            print("\n\nPreliminary Results (Quick Analysis):")
            self.display_current_best(self.quick_results, "Quick")
            self.quick_results_displayed = True
            
        if self.deep_results and not self.deep_results_displayed:
            print("\n\nRefined Results (Deep Analysis):")
            self.display_current_best(self.deep_results, "Deep")
            self.deep_results_displayed = True
            
        # Create and print progress line that updates in place
        sys.stdout.write(f"\rProgress - Quick: [{self.progress_bar(self.progress['quick'])}] {self.progress['quick']:.1f}% "
                        f"Deep: [{self.progress_bar(self.progress['deep'])}] {self.progress['deep']:.1f}%")
        sys.stdout.flush()
    
    def progress_bar(self, percentage, width=50):
        filled = int(width * percentage / 100)
        return '=' * filled + '-' * (width - filled)
    
    def display_current_best(self, results, analysis_type):
        if not results:
            return
            
        print("\nTop 3 Lineups:")
        
        # Only run detailed analysis if these are newly displayed results
        should_analyze = (analysis_type == "Quick" and not self.quick_results_displayed) or \
                        (analysis_type == "Deep" and not self.deep_results_displayed)
        
        if should_analyze:
            try:
                # Create a single simulator and metrics tracker for all lineups
                simulator = BaseballSimulator({name: self.players[name] for name in self.players})
                total_stats = MetricsTracker()
                
                # Pre-calculate all metrics to avoid interruption
                lineup_metrics = []
                for lineup, avg_runs in results:
                    # Reset metrics for each lineup
                    total_stats.reset()
                    
                    # Run 100 games for detailed analysis
                    for _ in range(100):
                        result = simulator.simulate_game(lineup)
                        total_stats.update_game_metrics(result)
                    
                    metrics = total_stats.get_game_metrics()
                    if metrics:  # Only add if metrics were calculated
                        lineup_metrics.append((lineup, avg_runs, metrics))
                
                # Buffer all output first
                output_buffer = []
                for i, (lineup, avg_runs, metrics) in enumerate(lineup_metrics, 1):
                    output_buffer.extend([
                        f"\n{i}. Average Runs: {avg_runs:.2f}",
                        f"   Lineup: {' -> '.join(lineup)}",
                        "\n   Detailed Statistics:",
                        f"   - Games Analyzed: 100",
                        f"   - 5-Run Innings: {metrics['five_run_innings']} ({metrics['five_run_inning_pct']*100:.1f}%)",
                        "\n   Inning-by-Inning Analysis:"
                    ])
                    
                    for inning, stats in enumerate(metrics['runs_by_inning'], 1):
                        output_buffer.extend([
                            f"   Inning {inning}:",
                            f"      Average Runs: {stats['avg']:.2f}",
                            f"      Max Runs: {stats['max']}",
                            f"      Scoreless: {stats['zero_run_pct']*100:.1f}%"
                        ])
                    
                    output_buffer.append("\n   " + "="*50)
                
                # Display all buffered output at once
                if output_buffer:
                    print('\n'.join(output_buffer))
                
            except Exception as e:
                print(f"\nError displaying results: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            # Just display basic info for already-shown results
            for i, (lineup, avg_runs) in enumerate(results, 1):
                print(f"\n{i}. Average Runs: {avg_runs:.2f}")
                print(f"   Lineup: {' -> '.join(lineup)}")

# Initialize with current player dictionary
playerDictionary = {"Jeremiah":[1,.9,[.6,.3,.1,0],0],
                   "Calvin":[0,.9,[.6,.3,.1,0],0],
                   "Ty":[0,.4,[.9,.1,0,0],0],
                   "Dean":[0,.6,[.9,.1,0,0],0],
                   "Harrison":[0,.2,[1,0,0,0],0],
                   "Kai":[0,.35,[.6,.3,.1,0],0],
                   "Theo":[0,.25,[.95,.05,0,0],0],
                   "Bob":[0,.80,[.8,.2,0,0],0],
                   "Joe":[0,.47,[1,0,0,0],0],
                   "Matt":[0,.60,[1,0,0,0],0],
                   "Arnold":[0,.50,[1,0,0,0],0]}

def main():
    try:
        # Initialize player manager
        manager = PlayerManager(playerDictionary)
        
        # Allow for updates
        manager.update_players()
        
        # Initialize parallel optimizer
        optimizer = ParallelOptimizer(manager.players)
        
        print("\nStarting lineup optimization...")
        quick_future, deep_future = optimizer.run_parallel_analysis()
        
        # Get quick results
        quick_results = quick_future.result()
        print("\nQuick Analysis Complete!")
        
        # Get deep results
        deep_results = deep_future.result()
        print("\nDeep Analysis Complete!")
        
        return quick_results, deep_results
        
    except KeyboardInterrupt:
        print("\nOptimization interrupted...")
        optimizer.running = False
        optimizer.keyboard_monitor.stop()
        # Allow the threads to complete their current work and save
        try:
            quick_results = quick_future.result(timeout=5)  # Wait up to 5 seconds
            deep_results = deep_future.result(timeout=5)
            return quick_results, deep_results
        except TimeoutError:
            print("\nTimeout waiting for results.")
            return None, None
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        return None, None

if __name__ == "__main__":
    main()
