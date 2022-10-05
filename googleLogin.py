class GoogleLogin:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.action_chains import ActionChains as _ActionChains
    from selenium.webdriver.common.keys import Keys as _Keys
    from selenium.webdriver.common.by import By as _By
    import time as _time
    import random as _random

    class PollReturnVal: pass

    def _poll(self,
            timeout: int,
            func: callable,
            expected_outcome,
            per_func_timeout: int = None,
            poll: int= 0.5
        ):
        error_logging = self.error_logging
        error_logger = self.logger

        def func_timeout(timeout, func, poll_time=0.5):
            import ctypes, time, threading

            class NoValSet:
                def __eq__(self, other): return (True if (type(other) == NoValSet) else False)

            class threadWithReturn(threading.Thread):
                def __init__(self, target):
                    super().__init__()
                    self.target, self._return = target, None
                def run(self):
                    self._return = self.target()
                def join(self):
                    super().join()
                    return self._return

            class waiter(threading.Thread):
                def __init__(self, *args, **kwargs):
                    super().__init__()
                    self.daemon = True
                    self.result = NoValSet()

                def run(self):
                    self.result = [thread.join() for thread in threadWithReturn(target=func).start()][0]

                def get_id(self):
                    if hasattr(self, '_thread_id'):
                        return self._thread_id
                    for id, thread in threading._active.items():
                        if thread is self:
                            return id
                def raise_exception(self):
                    if ctypes.pythonapi.PyThreadState_SetAsyncExc(self.get_id(), ctypes.py_object(SystemExit)) > 1:
                        ctypes.pythonapi.PyThreadState_SetAsyncExc(self.get_id(), 0)

            waiter_inst = waiter()
            waiter_inst.start()
            
            for _ in range(round(timeout//poll_time)):
                if waiter_inst.result != NoValSet():
                    return waiter_inst.result
                time.sleep(poll_time)

            waiter_inst.raise_exception()
            raise Exception("Function(%s) Timed out" % func.__name__)
        itr = 0
        import time
        while True:
            try:
                res = (lambda: func_timeout.func_timeout(per_func_timeout, func) if per_func_timeout != None else func() )()
                if (lambda: (not (res == expected_outcome)) if (expected_outcome != self.PollReturnVal) else False)():
                    raise RuntimeError("Unexpected OutCome")
                else:
                    return (lambda: res if (expected_outcome == self.PollReturnVal) else True)()
            except Exception as e:
                if timeout != None and itr == timeout*(poll**-1):
                    break
                if error_logging:
                    error_logger(f"Error: {type(e).__name__} was Triggered, Args: {e.args}")
                itr+=1
                time.sleep(poll)

    def __init__(self, username, password, headless=False):
        self.username = username
        self.password = password
        self.logger = print
        self.error_logging = True
        self._human_sleep: callable(int) = (lambda implicitTime: self._time.sleep(self._random.uniform((85.37/100)*implicitTime, (126.22/100)*implicitTime)))

        if headless and (os.name != 'nt'):
            from pyvirtualdisplay import Display
            self.display = Display(visible=False)
            self.display.start()
        elif headless:
            raise RuntimeError("Headless is only avalable on linux")

    def login(self)->uc.Chrome:
        self.driver = self.uc.Chrome()
        self.driver.get("https://accounts.google.com/ServiceLogin?service=accountsettings")

        assert self._poll(None, (lambda: self._ActionChains(self.driver).click(self.driver.find_element(self._By.CSS_SELECTOR, "#identifierId")).perform()), None)
        self._human_sleep(2)
        assert self._poll(None, (lambda: self._ActionChains(self.driver).send_keys(self.username).perform()), None)
        self._human_sleep(2)
        assert self._poll(None, (lambda: self._ActionChains(self.driver).send_keys(self._Keys.RETURN).perform()), None)

        assert self._poll(None, (lambda: self._ActionChains(self.driver).click(self.driver.find_element(self._By.CSS_SELECTOR, "#password > div.aCsJod.oJeWuf > div > div.Xb9hP > input")).perform() ), None)
        self._human_sleep(1)

        assert self._poll(None, (lambda: self._ActionChains(self.driver).send_keys(self.password).perform()), None)
        self._human_sleep(2)
        assert self._poll(None, (lambda: self._ActionChains(self.driver).send_keys(self._Keys.RETURN).perform()), None)
        self._human_sleep(4)

        return self.driver
