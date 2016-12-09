#!usr/bin/env python
#-*- coding: utf-8 -*-
import wx
import wx.grid
class GenericTable(wx.grid.PyGridTableBase):
    def __init__(self,data,rowLabels=0,colLabels=None):
        wx.grid.PyGridTableBase.__init__(self)
        self.data = data
        self.rowLabels = rowLabels
        self.colLabels = colLabels

    def GetNumberCols(self):
        return len(self.data[0])
    def GetNumberRows(self):
        return len(self.data)
    def GetColLabelValue(self,col):
        if self.colLabels:
            return self.colLabels[col]
    def GetRowLabelValue(self,row):
        if self.rowLabels:
            return self.rowLabels[row]
    def IsEmptyCell(self,row,col):
        return False
    def GetValue(self,row,col):
        return self.data[row][col]
    def SetValue(self,row,col,value):
        pass
class SimpleGrid(wx.grid.Grid):
    def __init__(self,parent,data,rowLabels=0,colLabels=None,pos=(0,50)):
        wx.grid.Grid.__init__(self,parent,-1,pos)
        tableBase = GenericTable(data,rowLabels,colLabels)
        self.SetTable(tableBase)