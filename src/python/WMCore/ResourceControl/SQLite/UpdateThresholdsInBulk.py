#!/usr/bin/env python
"""
_UpdateThresholdsInBulk_

This module updates thresholds for the given sites for SQLite
"""


from WMCore.ResourceControl.MySQL.UpdateThresholdsInBulk \
  import UpdateThresholdsInBulk as UpdateThresholdsInBulkMySQL
class UpdateThresholdsInBulk(UpdateThresholdsInBulkMySQL):
    pass
