from django.db import models

# Create your models here.
class CrudeRecord(models.Model):
    stream_id = models.IntegerField()
    seq = models.IntegerField()
    src = models.CharField(max_length=40)
    dst = models.CharField(max_length=40)
    tx = models.FloatField()
    rx = models.FloatField()
    size = models.IntegerField()
    hoplimit = models.IntegerField()

    def __str__(self):
        return f"{self.__class__.__name__} (id={self.id}, seq={self.seq}, src={self.src}, dst={self.dst}, tx={self.tx}, rx={self.rx}, size={self.size}, hoplimit={self.hoplimit})"



class Node(models.Model):
    ip = models.CharField(max_length=40)
    adr = models.CharField(max_length=40)


class Jitter(models.Model):
    from_ip = models.CharField(max_length=40)
    from_adr = models.CharField(max_length=40)
    to_ip = models.CharField(max_length=40)
    to_adr = models.CharField(max_length=40)
    datetime = models.DateTimeField()
    timestamp = models.FloatField()
    timestamp_zone = models.CharField(max_length=40, default="GMT")
    h_ddelay = models.FloatField()
    h_delay = models.FloatField()
    h_jit = models.FloatField()
    h_min_d = models.FloatField()
    h_n = models.IntegerField()
    h_slope_10 = models.FloatField()
    report_type = models.CharField(max_length=40)
    rdelay = models.TextField() # list[float] parse using json
    rtx = models.TextField() # list[float] parse using json
    slopes = models.TextField() # list[float] parse using json
    event_type = models.CharField(max_length=100, default='jitter', null=False)

    # proposals
    node = models.ForeignKey(Node, on_delete=models.SET_NULL, null=True)

class Gap(models.Model):
    from_ip = models.CharField(max_length=40)
    from_adr = models.CharField(max_length=40)
    to_ip = models.CharField(max_length=40)
    to_adr = models.CharField(max_length=40)
    datetime = models.DateTimeField()
    timestamp = models.FloatField()
    timestamp_zone = models.CharField(max_length=40, default="GMT")
    h_ddelay = models.FloatField()
    h_delay = models.FloatField()
    h_jit = models.FloatField()
    h_min_d = models.FloatField()
    h_n = models.IntegerField()
    h_slope_10 = models.FloatField()
    h_slope_20 = models.FloatField()
    h_slope_30 = models.FloatField()
    h_slope_40 = models.FloatField()
    h_slope_50 = models.FloatField()
    overlap = models.IntegerField()
    t_ddelay = models.FloatField()
    t_delay = models.FloatField()
    t_jit = models.FloatField()
    t_min_d = models.FloatField()
    t_n = models.IntegerField()
    t_slope_10 = models.FloatField()
    t_slope_20 = models.FloatField()
    t_slope_30 = models.FloatField()
    t_slope_40 = models.FloatField()
    t_slope_50 = models.FloatField()
    tloss = models.FloatField()
    event_type = models.CharField(max_length=100, default='gap', null=False)

    # proposals
    GAP_CHOICES = [
        ('small', 'small'),
        ('big', 'big'),
    ]
    type = models.CharField(max_length=40, choices=GAP_CHOICES)
    node = models.ForeignKey(Node, on_delete=models.SET_NULL, null=True)



class GapSum(models.Model):
    from_ip = models.CharField(max_length=40)
    from_adr = models.CharField(max_length=40)
    to_ip = models.CharField(max_length=40)
    to_adr = models.CharField(max_length=40)
    datetime = models.DateTimeField()
    timestamp = models.FloatField()
    timestamp_zone = models.CharField(max_length=40, default="GMT")
    big_gaps = models.IntegerField()
    big_time = models.FloatField()
    small_gaps = models.IntegerField()
    small_time = models.FloatField()
    dTTL = models.FloatField()
    down_ppm = models.FloatField()
    duplicates = models.IntegerField()
    h_ddelay = models.FloatField()
    h_ddelay_sdv = models.FloatField()
    h_delay = models.FloatField()
    h_delay_sdv = models.FloatField()
    h_jit = models.FloatField()
    h_jit_sdv = models.FloatField()
    h_min_d = models.FloatField()
    h_min_d_sdv = models.FloatField()
    h_slope_10 = models.FloatField()
    h_slope_10_sdv = models.FloatField()
    lasted = models.TimeField()
    lasted_sec = models.FloatField()
    late = models.IntegerField()
    late_sec = models.FloatField()
    least_delay = models.FloatField()
    reordered = models.IntegerField()
    resets = models.IntegerField()
    event_type = models.CharField(max_length=100, default='gapsum', null=False)

    # proposals
    node = models.ForeignKey(Node, on_delete=models.SET_NULL, null=True)
