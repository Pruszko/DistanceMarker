package com.github.pruszko.distancemarker.config 
{
	import com.github.pruszko.distancemarker.utils.Disposable;

	public class Config implements Disposable
	{
		
		private var _decimalPrecision:int= 0;
		private var _textSize:int = 11;
		private var _textColor:int = 0xFFFFFF;
		private var _textAlpha:Number = 1.0;
		private var _drawTextShadow:Boolean = true;
		
		public function Config() 
		{
			super()
		}
		
		public function deserialize(serializedConfig:Object) : void
		{
			this._decimalPrecision = serializedConfig["decimal-precision"];
			this._textSize = serializedConfig["text-size"];
			this._textColor = serializedConfig["text-color"];
			this._textAlpha = serializedConfig["text-alpha"];
			this._drawTextShadow = serializedConfig["draw-text-shadow"];
		}
		
		public function disposeState() : void
		{
			
		}
		
		public function get decimalPrecision() : int
		{
			return this._decimalPrecision;
		}
		
		public function get textSize() : int
		{
			return this._textSize;
		}
		
		public function get textColor() : int
		{
			return this._textColor;
		}
		
		public function get textAlpha() : Number
		{
			return this._textAlpha;
		}
		
		public function get drawTextShadow() : Boolean
		{
			return this._drawTextShadow;
		}
		
	}

}