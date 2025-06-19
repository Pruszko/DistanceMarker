package com.github.pruszko.distancemarker.markers 
{
	import com.github.pruszko.distancemarker.config.Config;
	import com.github.pruszko.distancemarker.DistanceMarkerFlash;
	import com.github.pruszko.distancemarker.utils.Disposable;
	import flash.display.Shape;
	import flash.display.Sprite;
	import flash.filters.BlurFilter;
	import flash.filters.DropShadowFilter;
	import flash.filters.GlowFilter;
	import flash.text.AntiAliasType;
	import flash.text.TextField;
	import flash.text.TextFieldAutoSize;
	import flash.text.TextFieldType;
	import flash.text.TextFormat;

	public class DistanceMarker extends Sprite implements Disposable
	{

		private var _app:DistanceMarkerFlash;
		
		private var _currentDistance:Number = -1.0;
		
		private var _textField:TextField = new TextField();
		private var _shape:Shape;
		
		public function DistanceMarker(app:DistanceMarkerFlash) 
		{
			super()
			
			this._app = app;
			
			if (this.config.drawTextShadow)
			{
				this._shape = new Shape();
				this._shape.alpha = 0.35;
				this._shape.filters = [new BlurFilter(10, 10, 2)];
				this.addChild(this._shape);
			}
			
			this._textField.alpha = this.config.textAlpha;
			this._textField.antiAliasType = AntiAliasType.NORMAL;
			this._textField.autoSize = TextFieldAutoSize.CENTER;
			this._textField.background = false;
			this._textField.border = false;
			this._textField.multiline = false;
			this._textField.selectable = false;
			this._textField.type = TextFieldType.DYNAMIC;
			this._textField.wordWrap = false;
			this._textField.defaultTextFormat = new TextFormat("$TitleFont", this.config.textSize, this.config.textColor);
			
			if (this.config.drawTextOutline)
			{
				this._textField.filters = [new GlowFilter(0x000000, 1.0, 2, 2, 2, 2)];
			}
			
			var distanceUnit:String = this.config.drawDistanceUnit ? " m" : "";
			this._textField.text = "?" + distanceUnit;
			this._textField.x = -this._textField.textWidth / 2.0
						
			this.addChild(this._textField);
			
			if (this.config.drawTextShadow)
			{
				this.updateBackgroundShape();
			}
		}
		
		public function set currentDistance(currentDistance:Number) : void
		{	
			this._currentDistance = currentDistance;
			
			var distanceUnit:String = this.config.drawDistanceUnit ? " m" : "";
			this._textField.text = currentDistance.toFixed(this.config.decimalPrecision).toString() + distanceUnit;
			this._textField.x = -this._textField.textWidth / 2.0
			
			if (this.config.drawTextShadow)
			{
				this.updateBackgroundShape();
			}
		}
		
		private function updateBackgroundShape() : void
		{
			// I don't know why, but text bounding box is shifted by (2.0, 2.0) for some reason
			// why?
			// in any case - fix it manually
			var x:Number = this._textField.x + 2.0;
			var y:Number = this._textField.y + 2.0;
			var textWidth:Number = this._textField.textWidth;
			var textHeight:Number = this._textField.textHeight;
			var marginLR:Number = 10.0;
			var marginTB:Number = 2.0;
			
			this._shape.graphics.clear();
			this._shape.graphics.beginFill(0x000000);
			
			this._shape.graphics.drawEllipse(
				x - marginLR, y - marginTB,
				textWidth + (2.0 * marginLR), textHeight + (2.0 * marginTB)
			);
			
			this._shape.graphics.endFill();
		}
		
		public function get currentDistance() : Number
		{
			return this._currentDistance;
		}
		
		public function disposeState() : void
		{
			this.removeChild(this._textField);
			this._textField = null;
			
			if (this.config.drawTextShadow)
			{
				this.removeChild(this._shape);
				this._shape = null;
			}
			
			this._app = null;
		}
		
		public function isInBounds(mouseX:Number, mouseY:Number) : Boolean
		{
			return this._textField.hitTestPoint(mouseX, mouseY);
		}
		
		private function get config() : Config
		{
			return this._app.config;
		}
		
	}

}