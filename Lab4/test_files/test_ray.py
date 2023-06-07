import ray
import time

@ray.remote
class Compute:
    def __init__(self) -> None:
        self.count = 0

    def is_prime(self, n: int) -> bool:
        result = True
        for k in range(2, int(n ** 0.5) + 1):
            if n % k == 0:
                result = False
                break
        return result

    def count_primes(self, start: int, end: int, step: int) -> int:
        self.count = 0
        for k in range(start, end, step):
            if Compute.is_prime(k):
                self.count += 1
        return self.count
    
    def result(self):
        return self.count
    
def main():
    ray.init()
    init_time = time.time()
    # step: 指分组数，每一组内检查的数差值为step
    step = 10
    futures = []
    for i in range(step):
        computer = Compute.remote()
        future = computer.count_primes.remote(i, 10000000, step)
        futures.append(future)
    results = ray.get(futures)
    # 因为计算时把0和1也算入质数，因此在这里减去
    print(sum(results) - 2)
    '''
    computer = Compute.remote()
    futures = []
    future = computer.count_primes.remote(2, 10000000, 1)
    futures.append(future)
    result = ray.get(futures)
    print(result)
    '''
    print("total time: ", time.time()-init_time)

if __name__ == "__main__":
    main()
