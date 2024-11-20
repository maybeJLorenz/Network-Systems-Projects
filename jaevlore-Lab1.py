
import subprocess

## single function to mimic "traceroute" command
def traceroute(serverName):
    try:
        result = subprocess.run(['traceroute', serverName], capture_output = True, text = True, check = True, timeout = 20)
        print(result.stdout)

        hops = result.stdout.strip().split("\n")
        num_hops = len(hops) - 1
        print(f'{num_hops} hops to {serverName}')
    
    except subprocess.CalledProcessError as e: ## catches unreachable server
        print(f"Traceroute: failed")
    except subprocess.TimeoutExpired:          ## extra credit attempt: program timeout
        print(f"Traceroute: failed")
    except Exception as e:                     ## throws error if anything else goes wrong
        print(f"Traceroute: failed")

## main function
if __name__ == "__main__":
    userInput = input("Enter a server name: ")
    traceroute(userInput)
