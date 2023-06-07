import time

def is_prime(n: int):
    result = True
    for k in range(2, int(n ** 0.5) + 1):
        if n % k == 0:
            result = False
            break
    return result

def count_primes(n: int) -> int:
    count = 0
    for k in range(2, n):
        if is_prime(k):
            count += 1
    return count

def main():
    init_time = time.time()
    print(count_primes(10000000))
    print("total time: ", time.time()-init_time)

if __name__ == "__main__":
    main()