// Copyright (c) Ognyan Moore
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel,
  DOMWidgetView,
  ISerializers,
} from '@jupyter-widgets/base';

import { MODULE_NAME, MODULE_VERSION } from './version';

// Import the CSS
import '../css/widget.css';

export class EptiumModel extends DOMWidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: EptiumModel.model_name,
      _model_module: EptiumModel.model_module,
      _model_module_version: EptiumModel.model_module_version,
      _view_name: EptiumModel.view_name,
      _view_module: EptiumModel.view_module,
      _view_module_version: EptiumModel.view_module_version,
      src: 'https://viewer.copc.io',
    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
    // Add any extra serializers here
  };

  static model_name = 'EptiumModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'EptiumView'; // Set to null if no view
  static view_module = MODULE_NAME; // Set to null if no view
  static view_module_version = MODULE_VERSION;
}

export class EptiumView extends DOMWidgetView {
  private _iframe: HTMLIFrameElement;

  render() {
    this._iframe = document.createElement('iframe');
    this._iframe.width = '100%';
    this._iframe.height = '400';
    this._iframe.style.boxSizing = 'border-box';
    this._iframe.style.border = '4px solid red';

    // this.el is the DOM element associated with the view
    this.el.appendChild(this._iframe);
    this._onSrcChanged();

    // Python -> TypeScript update
    this.model.on('change:src', this._onSrcChanged, this);
  }

  private _onSrcChanged() {
    const url = this.model.get('src');
    this.model.widget_manager.resolveUrl(url).then((resolvedUrl) => {
      this._iframe.src = resolvedUrl;
    });
  }
}
