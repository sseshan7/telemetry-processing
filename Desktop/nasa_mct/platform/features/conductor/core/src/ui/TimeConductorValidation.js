/*****************************************************************************
 * Open MCT Web, Copyright (c) 2014-2015, United States Government
 * as represented by the Administrator of the National Aeronautics and Space
 * Administration. All rights reserved.
 *
 * Open MCT Web is licensed under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://www.apache.org/licenses/LICENSE-2.0.
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 *
 * Open MCT Web includes source code licensed under additional open source
 * licenses. See the Open Source Licenses file (LICENSES.md) included with
 * this source code distribution or the Licensing information page available
 * at runtime from the About dialog for additional information.
 *****************************************************************************/

define(
    [],
    function () {

        /**
         * Form validation for the TimeConductorController.
         * @param conductor
         * @constructor
         */
        function TimeConductorValidation(timeAPI) {
            var self = this;
            this.timeAPI = timeAPI;

            /*
             * Bind all class functions to 'this'
             */
            Object.keys(TimeConductorValidation.prototype).filter(function (key) {
                return typeof TimeConductorValidation.prototype[key] === 'function';
            }).forEach(function (key) {
                self[key] = self[key].bind(self);
            });
        }

        /**
         * Validation methods below are invoked directly from controls in the TimeConductor form
         */
        TimeConductorValidation.prototype.validateStart = function (start) {
            var bounds = this.timeAPI.bounds();
            return this.timeAPI.validateBounds({start: start, end: bounds.end}) === true;
        };

        TimeConductorValidation.prototype.validateEnd = function (end) {
            var bounds = this.timeAPI.bounds();
            return this.timeAPI.validateBounds({start: bounds.start, end: end}) === true;
        };

        TimeConductorValidation.prototype.validateStartOffset = function (startOffset) {
            return !isNaN(startOffset) && startOffset > 0;
        };

        TimeConductorValidation.prototype.validateEndOffset = function (endOffset) {
            return !isNaN(endOffset) && endOffset >= 0;
        };

        return TimeConductorValidation;
    }
);
