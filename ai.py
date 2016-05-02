#coding:utf-8
import Queue
import random
import time
import multiprocessing

DIR_UP = 0
DIR_RIGHT = 1
DIR_DOWN = 2
DIR_LEFT = 3
DIR_NONE = 4

class ai_agent():
  mapinfo = []
  shoot = 1
  move_dir = DIR_NONE
  lastPlayerRect = [0, 0, 0, 0]
  deadlockCounter = 0
  directionHistory = []

  def __init__(self):
    self.mapinfo = []

  # rect:         [left, top, width, height]
  # rect_type:      0:empty 1:brick 2:steel 3:water 4:grass 5:froze
  # castle_rect:      [12*16, 24*16, 32, 32]
  # mapinfo[0]:       bullets [rect, direction, speed]]
  # mapinfo[1]:       enemies [rect, direction, speed, type]]
  # enemy_type:     0:TYPE_BASIC 1:TYPE_FAST 2:TYPE_POWER 3:TYPE_ARMOR
  # mapinfo[2]:       tile  [rect, type] (empty don't be stored to mapinfo[2])
  # mapinfo[3]:       player  [rect, direction, speed, Is_shielded]]
  # shoot:        0:none 1:shoot
  # move_dir:       0:Up 1:Right 2:Down 3:Left 4:None
  # keep_action:      0:The tank work only when you Update_Strategy.  1:the tank keep do previous action until new Update_Strategy.

  # def Get_mapInfo:    fetch the map infomation
  # def Update_Strategy Update your strategy

  def delay(self):
    time.sleep(0.01)

  def operations (self,p_mapinfo,c_control):
    while True:
    #-----your ai operation,This code is a random strategy,please design your ai !!-----------------------
      self.Get_mapInfo(p_mapinfo)
      self.delay()

      # shoot = 0
      # move_dir = random.randint(0,3)

      self.bullets = self.mapinfo[0]
      self.enemies = self.mapinfo[1]
      self.player = self.mapinfo[3][0]
      self.castle = [[12*16, 24*16, 32, 32], 4, 0, 4]

      self.move_dir = random.randint(0,3)
      self.performAttack()
      self.performAvoidCastle()
      self.performAvoidBullets()
      self.performAvoidDeadlock()
      print ''

      keep_action = 0
      #-----------
      self.Update_Strategy(c_control,self.shoot,self.move_dir,keep_action)
    #------------------------------------------------------------------------------------------------------

  def performAttack(self):
    closestPlayerEnemy = self.getClosestBlock(self.player, self.enemies)
    closestCastleEnemy = self.getClosestBlock(self.castle, self.enemies)

    if closestCastleEnemy is not None:
      direction2D = self.getRelativeDirection2D(self.player, closestCastleEnemy)
      self.move_dir = self.getRandomDirection(direction2D)
      self.shoot = 1
      print '[target enemy - castle] go', self.directionToString(self.move_dir)

    if closestPlayerEnemy is not None:
      distanceSquare = self.getDistanceSquare(self.player, closestPlayerEnemy)
      if distanceSquare < (16*5)**2 + (16*5)**2:
        direction2D = self.getRelativeDirection2D(self.player, closestPlayerEnemy)
        # if closestPlayerEnemy[1] == DIR_UP or closestPlayerEnemy[1] == DIR_DOWN:
        #   self.move_dir = direction2D[0]
        # else:
        #   self.move_dir = direction2D[1]
        if distanceSquare < (16*3)**2 + (16*3)**2:
          # self.move_dir = DIR_NONE
          self.move_dir = self.getRelativeDirection(self.player, closestPlayerEnemy)
        else:
          self.move_dir = self.getRandomDirection(direction2D)
        self.shoot = 1
        print '[target enemy - player] go', self.directionToString(self.move_dir)

  def performAvoidCastle(self):
    castleInView = self.getBlocksFromView(self.player, [self.castle], 16*3)
    if len(castleInView) > 0:
      shoot = 1
      castleDirection = self.getRelativeDirection(self.player, self.castle)
      castleDirection2D = self.getRelativeDirection2D(self.player, self.castle)
      # if castleDirection == DIR_LEFT:
      #   self.move_dir = DIR_UP
      # elif castleDirection == DIR_RIGHT:
      #   self.move_dir = DIR_UP
      # elif castleDirection == DIR_DOWN:
      #   self.move_dir = self.getRandomDirection([DIR_UP, DIR_LEFT, DIR_RIGHT])
      if self.move_dir == castleDirection or self.move_dir == DIR_NONE or self.move_dir == DIR_DOWN:
        if castleDirection == DIR_LEFT:
          # self.move_dir = self.getRandomDirection([DIR_UP, DIR_RIGHT])
          self.move_dir = DIR_UP
        elif castleDirection == DIR_RIGHT:
          # self.move_dir = self.getRandomDirection([DIR_UP, DIR_LEFT])
          self.move_dir = DIR_UP
        elif castleDirection == DIR_DOWN:
          self.move_dir = self.getRandomDirection([DIR_UP, DIR_LEFT, DIR_RIGHT])
          # if castleDirection2D[0] == DIR_LEFT:
          #   self.move_dir = self.getRandomDirection([DIR_UP, DIR_LEFT])
          # if castleDirection2D[0] == DIR_RIGHT:
          #   self.move_dir = self.getRandomDirection([DIR_UP, DIR_RIGHT])
      # else:
      #   self.move_dir = self.getRandomMutexDirection([castleDirection])
      #   if castleDirection == DIR_LEFT:
      #     self.move_dir = DIR_UP
      #   elif castleDirection == DIR_RIGHT:
      #     self.move_dir = DIR_UP
      #   elif castleDirection == DIR_DOWN:
      #     self.move_dir = self.getRandomDirection([DIR_UP, DIR_LEFT, DIR_RIGHT])
      print '[detect castle] castle dir =', self.directionToString(castleDirection), 'go', self.directionToString(self.move_dir)
    # else:
    #   print '[no castle]'

  def performAvoidBullets(self):
      bulletsInView = self.getBlocksFromView(self.player, self.bullets, 16*0.5)
      bulletDirections = self.getRelativeDirections(self.player, bulletsInView)

      if len(bulletsInView) > 0:
        bullet = bulletsInView[0]
        bulletDirection = bullet[1]
        relDirection = bulletDirections[0]
        if (bulletDirection != relDirection):
          self.shoot = 1
          self.move_dir = relDirection
          print '[bullet in view] hit', self.directionToString(self.move_dir)
        # if (bulletDirection == DIR_DOWN and relDirection == DIR_UP) or (bulletDirection == DIR_UP and relDirection == DIR_DOWN):
        #   self.move_dir = self.getRandomDirection([DIR_LEFT, DIR_RIGHT])
        # elif (bulletDirection == DIR_RIGHT and relDirection == DIR_LEFT) or (bulletDirection == DIR_LEFT and relDirection == DIR_RIGHT):
        #   self.move_dir = self.getRandomDirection([DIR_UP, DIR_DOWN])

      # if len(bulletsInView) == 1 and bulletDirections[0] == player[1]:
      #   move_dir = random.randint(0,3)
      #   print '[self\'s bullet in region] go', self.directionToString(move_dir)
      # else:
      #   # move_dir = self.getRandomMutexDirection(bulletDirections)
      #   move_dir = random.randint(0,3)
      #   print '[bullet in region] go', self.directionToString(move_dir)

  def performAvoidDeadlock(self):
    player = self.player
    playerRect = player[0]
    playerDirection = player[1]
    if playerRect == self.lastPlayerRect:
      self.deadlockCounter = self.deadlockCounter + 1
      if playerDirection not in self.directionHistory:
        self.directionHistory.append(playerDirection)
    if self.deadlockCounter > 200:
      self.deadlockCounter = 0
      self.directionHistory = []
      self.move_dir = self.getRandomMutexDirection(self.directionHistory)
      print '[deadlick] go', self.directionToString(self.move_dir)
    self.lastPlayerRect = playerRect

  def getDistanceSquare(self, center, block):
    centerRect = center[0]
    blockRect = block[0]
    distanceSquare = (centerRect[0] - blockRect[0])**2 + (centerRect[1] - blockRect[1])**2
    return distanceSquare

  def getClosestBlock(self, center, blocks):
    minDistanceSquare = 9999999999
    selectedBlock = None
    for block in blocks:
      distanceSquare = self.getDistanceSquare(center, block)
      if (distanceSquare < minDistanceSquare):
        minDistanceSquare = distanceSquare
        selectedBlock = block
    return selectedBlock

  def getRandomMutexDirection(self, exceptDirections):
    mutexDirections = self.getMutexDirections(exceptDirections)
    if len(mutexDirections) == 0:
      return random.randint(0,3)
    else:
      randomMutexDirection = self.getRandomDirection(mutexDirections)
      return randomMutexDirection

  def getMutexDirections(self, exceptDirections):
    allDirections = range(0, 4) # [0, 1, 2, 3]
    for d in exceptDirections:
      if d in allDirections:
        allDirections.remove(d)
    return allDirections

  def getRandomDirection(self, directions):
    length = len(directions)
    index = random.randint(0, length - 1)
    return directions[index]

  def directionToString(self, direction):
    return ['^', '>', 'v', '<', 'x'][direction]

  def getBlocksFromRegion(self, center, blocks, margin):
    r = []
    centerRect = center[0]
    centerLeftBound = centerRect[0] - margin
    centerTopBound = centerRect[1] - margin
    centerRightBound = centerRect[0] + centerRect[2] + margin
    centerBottomBound = centerRect[1] + centerRect[3] + margin
    for block in blocks:
      blockRect = block[0]
      blockLeftBound = blockRect[0]
      blockTopBound = blockRect[1]
      blockRightBound = blockRect[0] + blockRect[2]
      blockBottomBound = blockRect[1] + blockRect[3]
      if (centerLeftBound < blockLeftBound and blockRightBound < centerRightBound) and (centerTopBound < blockTopBound and blockBottomBound < centerBottomBound):
        r.append(block)
    return r

  def getBlocksFromView(self, center, blocks, margin):
    r = []
    centerRect = center[0]
    centerLeftBound = centerRect[0] - margin
    centerTopBound = centerRect[1] - margin
    centerRightBound = centerRect[0] + centerRect[2] + margin
    centerBottomBound = centerRect[1] + centerRect[3] + margin
    for block in blocks:
      blockRect = block[0]
      blockLeftBound = blockRect[0]
      blockTopBound = blockRect[1]
      blockRightBound = blockRect[0] + blockRect[2]
      blockBottomBound = blockRect[1] + blockRect[3]
      if (centerLeftBound < blockLeftBound and blockRightBound < centerRightBound) or (centerTopBound < blockTopBound and blockBottomBound < centerBottomBound):
        r.append(block)
    return r

  def matchPlayerAndBlocks(self, player, blocks, innerPadding = 0):
    playerRect = player[0]
    playerLeftBound = playerRect[0] + innerPadding
    playerTopBound = playerRect[1] + innerPadding
    playerRightBound = playerRect[0] + playerRect[2] - innerPadding
    playerBottomBound = playerRect[1] + playerRect[3] - innerPadding

    for block in blocks:
      blockRect = block[0]
      blockLeftBound = blockRect[0]
      blockTopBound = blockRect[1]
      blockRightBound = blockRect[0] + blockRect[2]
      blockBottomBound = blockRect[1] + blockRect[3]

      # block is on player's vertical view
      if (playerLeftBound < blockLeftBound and blockLeftBound < playerRightBound) or (playerLeftBound < blockRightBound and blockRightBound < playerRightBound):
        if (blockBottomBound < playerTopBound):
          return True, 0, block
        else:
          return True, 2, block

      # block is on player's horizontal view
      elif (playerTopBound < blockBottomBound and blockBottomBound < playerBottomBound) or (playerTopBound < blockTopBound and blockTopBound < playerBottomBound):
        if (blockRightBound < playerLeftBound):
          return True, 3, block
        else:
          return True, 1, block

    return False, 4, None

  def getRelativeDirections(self, center, blocks):
    r = []
    for block in blocks:
      r.append(self.getRelativeDirection(center, block))
    return r

  def getRelativeDirection2D(self, center, block):
    centerRect = center[0]
    centerLeftBound = centerRect[0]
    centerTopBound = centerRect[1]
    centerRightBound = centerRect[0] + centerRect[2]
    centerBottomBound = centerRect[1] + centerRect[3]
    centerCenterX = (centerLeftBound + centerRightBound) / 2
    centerCenterY = (centerTopBound + centerBottomBound) / 2

    blockRect = block[0]
    blockLeftBound = blockRect[0]
    blockTopBound = blockRect[1]
    blockRightBound = blockRect[0] + blockRect[2]
    blockBottomBound = blockRect[1] + blockRect[3]
    blockCenterX = (blockLeftBound + blockRightBound) / 2
    blockCenterY = (blockTopBound + blockBottomBound) / 2

    dirs = [0, 0] # [left/right, up/down]
    xDiff = centerCenterX - blockCenterX
    yDiff = centerCenterY - blockCenterY
    if xDiff < 0:
      dirs[0] = DIR_RIGHT
    else:
      dirs[0] = DIR_LEFT

    if (yDiff < 0):
      dirs[1] = DIR_DOWN
    else:
      dirs[1] = DIR_UP

    return dirs

  def getRelativeDirection(self, center, block):
    centerRect = center[0]
    centerLeftBound = centerRect[0]
    centerTopBound = centerRect[1]
    centerRightBound = centerRect[0] + centerRect[2]
    centerBottomBound = centerRect[1] + centerRect[3]
    centerCenterX = (centerLeftBound + centerRightBound) / 2
    centerCenterY = (centerTopBound + centerBottomBound) / 2

    blockRect = block[0]
    blockLeftBound = blockRect[0]
    blockTopBound = blockRect[1]
    blockRightBound = blockRect[0] + blockRect[2]
    blockBottomBound = blockRect[1] + blockRect[3]
    blockCenterX = (blockLeftBound + blockRightBound) / 2
    blockCenterY = (blockTopBound + blockBottomBound) / 2

    dirs = [0, 0] # [left/right, up/down]
    xDiff = centerCenterX - blockCenterX
    yDiff = centerCenterY - blockCenterY
    if xDiff < 0:
      dirs[0] = DIR_RIGHT
    else:
      dirs[0] = DIR_LEFT

    if (yDiff < 0):
      dirs[1] = DIR_DOWN
    else:
      dirs[1] = DIR_UP

    if abs(xDiff) > abs(yDiff):
      return dirs[0]
    else:
      return dirs[1]

  def Get_mapInfo(self,p_mapinfo):
    if p_mapinfo.empty()!=True:
      try:
        self.mapinfo = p_mapinfo.get(False)
      except Queue.Empty:
        skip_this=True

  def Update_Strategy(self,c_control,shoot,move_dir,keep_action):
    if c_control.empty() ==True:
      c_control.put([shoot,move_dir,keep_action])
      return True
    else:
      return False