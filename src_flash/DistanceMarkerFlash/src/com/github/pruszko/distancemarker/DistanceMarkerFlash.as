package com.github.pruszko.distancemarker
{

	import com.github.pruszko.distancemarker.config.Config;
	import com.github.pruszko.distancemarker.markers.DistanceMarker;
	import flash.display.Sprite;
	import flash.events.Event;
	
	public class DistanceMarkerFlash extends Sprite 
	{
		
		private static const SWF_HALF_WIDTH:Number = 400;
		private static const SWF_HALF_HEIGHT:Number = 300;
		
		private static const DISTANCE_REFRESH_INTERVAL:int = 12;
		private static const DISTANCE_DEPTH_SORT_INTERVAL:int = 60;
		
		// Python-side method required for in-between game state updates
		public var py_requestFrameData:Function;
		
		private var _config:Config = new Config();
		
		private var _updateDistanceCountdown:int = 1;
		private var _sortByDistanceCountdown:int = 1;

		public function DistanceMarkerFlash() 
		{
			super();
		}
		
		public function as_populate() : void
		{
			this.addEventListener(Event.ENTER_FRAME, this.onEnterFrame);
		}
		
		public function as_dispose() : void
		{
			this.removeEventListener(Event.ENTER_FRAME, this.onEnterFrame);
			
			for (var i:int = 0; i < numChildren; ++i) {
				var marker:DistanceMarker = getMarkerAt(i);
				marker.disposeState();
			}
			
			this.removeChildren();
			
			this._config.disposeState();
			this._config = null;
		}
		
		private function onEnterFrame() : void
		{
			if (this.py_requestFrameData == null)
			{
				return;
			}
			
			var serializedFrameData:Object = this.py_requestFrameData();
			
			this.updateAppPosition(serializedFrameData);
			this.updateMarkers(serializedFrameData);
			
			var observedVehicles:Array = serializedFrameData["observedVehicles"];
			observedVehicles.splice(0, observedVehicles.length);
		}
		
		public function as_applyConfig(serializedConfig:Object) : void
		{
			this._config.deserialize(serializedConfig);
		}
		
		public function as_isPointInMarker(mouseX:Number, mouseY:Number) : Boolean
		{
			// offset tested position by current position
			mouseX += this.x;
			mouseY += this.y;
			
			for (var i:int = 0; i < this.numChildren; ++i)
			{
				var marker:DistanceMarker = this.getMarkerAt(i);
				
				if (marker.isInBounds(mouseX, mouseY))
				{
					return true;
				}
			}
			return false;
		}
		
		private function updateAppPosition(serializedFrameData:Object) : void
		{	
			// Update flash app position to exactly top-left corner
			var appWidth:int = serializedFrameData["screenWidth"];
			var appHeight:int = serializedFrameData["screenHeight"];
			
			// This is based on updatePosition() from battleDamageIndicatorApp.swf
			// because it is the only source of "something is working" stuff 
			// and "visible in code" stuff when it comes to GUI.Flash
			//
			// Basically, our flash app center is positioned in the middle of the screen
			// with width and height declared in swf file
			// and despite having settings to change this behavior (position, size, anchors, etc)
			// from python-side on GUI.Flash, those does not work at all, lmao
			// 
			// To fix it ourselves, we have to:
			// - add half size of swf to anchor it to its left top corner in the middle of the screen
			// - substract half of the screen to move it to left top corner of the screen
			// 
			// Those changes MUST be done on flash object itself, not on GUI.Flash component
			this.x = SWF_HALF_WIDTH - (appWidth / 2.0);
			this.y = SWF_HALF_HEIGHT - (appHeight / 2.0);
		}
		
		private function updateMarkers(serializedFrameData:Object) : void
		{
			var observedVehicles:Array = serializedFrameData["observedVehicles"];
			
			// do nothing if there are no markers present and no markers to show
			if (this.numChildren == 0 && observedVehicles.length == 0)
			{
				return;
			}
			
			this.destroyInvalidMarkers(observedVehicles);
			this.createOrUpdateMarkers(observedVehicles);
			
			// sort markers by distance every certain interval
			if (--this._sortByDistanceCountdown <= 0)
			{
				this._sortByDistanceCountdown = DISTANCE_DEPTH_SORT_INTERVAL;
				this.sortMarkersByDistance();
			}
		}
		
		private function destroyInvalidMarkers(observedVehicles:Array) : void
		{			
			nextMarkerLabel:
			for (var i:int = 0; i < this.numChildren;)
			{
				var marker:DistanceMarker = this.getMarkerAt(i);
				
				for (var j:int = 0; j < observedVehicles.length; ++j)
				{
					if (marker.name == observedVehicles[j]["id"])
					{
						i += 1;
						continue nextMarkerLabel;
					}
				}
				
				this.removeChildAt(i);
				marker.disposeState();
			}
		}
		
		private function createOrUpdateMarkers(observedVehicles:Array) : void
		{
			// update distance text every certain interval
			var shouldRefreshDistance:Boolean = false;
			if (--this._updateDistanceCountdown <= 0)
			{
				this._updateDistanceCountdown = DISTANCE_REFRESH_INTERVAL;
				shouldRefreshDistance = true;
			}
			
			// Update all markers to proper 2d position starting from left-corner
			// also update their visibility in screen
			for (var i:int = 0; i < observedVehicles.length; ++i)
			{
				var observedVehicle:Object = observedVehicles[i];
				
				// implicitly create markers for newly seen vehicles
				// this also invalidates distance sorting on creation
				var marker:DistanceMarker = this.getOrCreateMarkerById(observedVehicle["id"]);
				
				var currentDistance:Number = observedVehicle["currentDistance"];
				var x:Number = observedVehicle["x"];
				var y:Number = observedVehicle["y"];
				var isVisible:Boolean = observedVehicle["isVisible"];
				
				// new markers have negative distance, so they will be immediately updated
				if (shouldRefreshDistance || marker.currentDistance < 0.0)
				{
					marker.currentDistance = currentDistance;
				}
				
				marker.x = x;
				marker.y = y;
				
				if (marker.visible != isVisible)
				{
					marker.visible = isVisible;
				}
			}
		}
		
		private function sortMarkersByDistance() : void
		{
			// using insertion sort due to few pros:
			// - in almost-best cases (ex. marker added at the end) it has close to O(n) complexity
			// - it doesn't require any data structures
			for(var i:int = 1; i < this.numChildren; i++) {
				var j:int = i;
				
				// further markers should be displayed first
				// to be covered by closer ones
				while (j > 0 && getMarkerAt(j - 1).currentDistance < getMarkerAt(j).currentDistance) {
					this.swapChildrenAt( j - 1, j );
					--j;
				}
			}
		}
		
		private function getMarkerAt(index:int) : DistanceMarker
		{
			return this.getChildAt(index) as DistanceMarker;
		}
		
		private function getOrCreateMarkerById(vehicleID:String) : DistanceMarker
		{
			var marker:DistanceMarker = this.getChildByName(vehicleID) as DistanceMarker;
			if (marker != null)
			{
				return marker;
			}
			
			marker = new DistanceMarker(this);
			marker.name = vehicleID;
			
			this.addChild(marker);
			
			this._sortByDistanceCountdown = 1;
			
			return marker;
		}
		
		public function get config() : Config
		{
			return this._config;
		}
		
	}
	
}