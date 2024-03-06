package com.github.pruszko.distancemarker.markers 
{
	import com.github.pruszko.distancemarker.config.Config;
	import com.github.pruszko.distancemarker.DistanceMarkerFlash;
	import com.github.pruszko.distancemarker.utils.Disposable;
	import flash.display.Shape;
	import flash.display.Sprite;
	import flash.filters.BlurFilter;
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
			
			this._textField.alpha = this.config.textAlpha
			this._textField.antiAliasType = AntiAliasType.NORMAL;
			this._textField.autoSize = TextFieldAutoSize.CENTER;
			this._textField.background = false;
			this._textField.border = false;
			this._textField.multiline = false;
			this._textField.selectable = false;
			this._textField.type = TextFieldType.DYNAMIC;
			this._textField.wordWrap = false;
			this._textField.defaultTextFormat = new TextFormat("$TitleFont", this.config.textSize, this.config.textColor);
			
			this._textField.text = "? m";
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
			
			this._textField.text = currentDistance.toFixed(this.config.decimalPrecision).toString() + " m";
			this._textField.x = -this._textField.textWidth / 2.0
			
			if (this.config.drawTextShadow)
			{
				this.updateBackgroundShape();
			}
		}
		
		private function updateBackgroundShape() : void
		{
			var textWidth:Number = this._textField.textWidth + 4.0;
			var textHeight:Number = this._textField.textHeight + 4.0;
			
			this._shape.graphics.clear();
			this._shape.graphics.beginFill(0x000000);
			
			this._shape.graphics.drawEllipse(-8.0 - (textWidth / 2.0), 0.0, textWidth + 16.0, textHeight);
			
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