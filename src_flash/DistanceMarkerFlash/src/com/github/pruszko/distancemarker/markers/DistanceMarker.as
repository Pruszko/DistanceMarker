package com.github.pruszko.distancemarker.markers 
{
	import com.github.pruszko.distancemarker.utils.Disposable;
	import flash.display.Shape;
	import flash.display.Sprite;
	import flash.filters.BlurFilter;
	import flash.text.TextField;
	import flash.text.TextFieldAutoSize;
	import flash.text.TextFieldType;
	import flash.text.TextFormat;

	public class DistanceMarker extends Sprite implements Disposable
	{

		private var _currentDistance:Number = -1.0;
		
		private var _textField:TextField = new TextField();
		private var _shape:Shape = new Shape();
		
		public function DistanceMarker() 
		{
			super()
			
			this.alpha = 0.8;
			
			this._shape.alpha = 0.6;
			this._shape.filters = [new BlurFilter(10, 10, 2)];
			this.addChild(this._shape);
			
			this._textField.autoSize = TextFieldAutoSize.CENTER;
			this._textField.background = false;
			this._textField.border = false;
			this._textField.multiline = false;
			this._textField.selectable = false;
			this._textField.type = TextFieldType.DYNAMIC;
			this._textField.wordWrap = false;
			this._textField.defaultTextFormat = new TextFormat("$FieldFont", 12, 0xFFFFFF);
			
			this._textField.text = "? m";
			this._textField.x = -this._textField.textWidth / 2.0
						
			this.addChild(this._textField);
			
			this.updateBackgroundShape();
		}
		
		public function set currentDistance(currentDistance:Number) : void
		{	
			this._currentDistance = currentDistance;
			
			this._textField.text = currentDistance.toFixed(2).toString() + " m";
			this._textField.x = -this._textField.textWidth / 2.0
			
			this.updateBackgroundShape();
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
			
			this.removeChild(this._shape);
		}
		
	}

}