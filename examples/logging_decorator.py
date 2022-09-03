from simple_eff import Effect, eff

log = Effect()


@eff
def plus_one(a: int):
    yield log.perform(a)
    return a + 1


def handle_log(k, v):
    print(f"Input value: {v}")
    return k(None)


if __name__ == "__main__":
    eleven = plus_one(10)
    eleven.on(log, handle_log)
    ret = eleven.run()
    print(ret)
