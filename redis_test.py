# quick test of redis - server installed as daemon
import redis
import threading
import time


class Listener(threading.Thread):
    def __init__(self, r, channels):
        threading.Thread.__init__(self)
        self.redis = r
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)
    
    def work(self, item):
        print item['channel'], ":", item['data']
    
    def run(self):
        while True:
            item = self.pubsub.get_message()
            if item == None:
                print("Thread Sleeping ...")
                time.sleep(1)
            else:
                if item['data'] == "KILL":
                    self.pubsub.unsubscribe()
                    print self, "unsubscribed and finished"
                    break
                else:
                    self.work(item)

if __name__ == "__main__":
    rdb = redis.Redis(host='localhost', port=6379, db=0)
    rdb.set('a_key','the_value')
    result = rdb.get('a_key')
    print ("Result should be 'the_value': {0}".format(result))

    client = Listener(rdb, ['test'])
    client.start()
    
    rdb.publish('test', 'this will reach the listener')
    rdb.publish('fail', 'this will not')
    print("Main Sleeping For 10 Seconds")
    time.sleep(10)
    rdb.publish('test', 'KILL')