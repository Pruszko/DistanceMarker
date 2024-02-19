package com.github.pruszko.distancemarker.markers 
{
	import com.github.pruszko.distancemarker.utils.Disposable;
	import flash.display.Sprite;
	import flash.globalization.LocaleID;
	import flash.globalization.NumberFormatter;
	import flash.text.TextField;
	import flash.text.TextFieldAutoSize;
	import flash.text.TextFieldType;
	import flash.text.TextFormat;

	public class DistanceMarker extends Sprite implements Disposable
	{

		private var _currentDistance:Number = -1.0;
		private var _textField:TextField = new TextField();
		
		public function DistanceMarker() 
		{
			super()
			
			this.alpha = 0.8;
			
			this._textField.autoSize = TextFieldAutoSize.CENTER;
			this._textField.background = true;
			this._textField.backgroundColor = 0x222222;
			this._textField.border = false;
			this._textField.multiline = false;
			this._textField.selectable = false;
			this._textField.textColor = 0xFFFFFF;
			this._textField.type = TextFieldType.DYNAMIC;
			this._textField.wordWrap = false;
			
			this._textField.text = "? m";
			this._textField.x = -this._textField.textWidth / 2.0
						
			this.addChild(_textField);
		}
		
		public function set currentDistance(currentDistance:Number) : void
		{	
			this._currentDistance = currentDistance;
			
			this._textField.text = currentDistance.toFixed(2).toString() + " m";
			this._textField.x = -this._textField.textWidth / 2.0
		}
		
		public function get currentDistance() : Number
		{
			return this._currentDistance;
		}
		
		public function disposeState() : void
		{
			removeChild(_textField);
			this._textField = null;
		}
		
	}

}