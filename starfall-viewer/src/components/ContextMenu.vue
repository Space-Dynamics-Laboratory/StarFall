<!-- 
# ------------------------------------------------------------------------
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# ------------------------------------------------------------------------
-->

 <template>
  <div
    class="fixed z-index"
    :class="isOpen ? '' : 'invisible'"
    ref="container"
    :style="styling"
  >
    <slot />
  </div>
</template>

<script lang="ts">
/**
 * Context Menu component.
 *
 * Example usage:
 *
 * Add a left click handler to the target element for which you want a context menu:
 *
 * <div @click.native="openMenu($event)" />
 *
 * For right click, handle the contextmenu event:
 *
 * <div @contextmenu.prevent="openMenu($event)" />
 *
 * Add a context menu with a ref tag:
 *
 * <ContextMenu ref="myContextMenu">
 *   <div>
 *     <div @click.native="onContextClick(1)">#1</div>
 *     <div @click.native="onContextClick(2)">#2</div>
 *     <div @click.native="onContextClick(3)">#3</div>
 *   </div>
 * </ContextMenu>
 *
 * Open the context menu from target element click handler:
 *
 * openMenu(event : MouseEvent) {
 *   const menu = this.$refs.myContextMenu as any;
 *   menu.open(event);
 * }
 *
 * The context menu can also be closed programmatically via the close method:
 *
 * closeMenu() {
 *   const menu = this.$refs.myContextMenu as any;
 *   menu.close();
 * }
 */
export default {
  name: 'ContextMenu',
  computed: {
    isLeftOfCenter(): boolean {
      return this.xPosition < this.xMidpoint
    },
    isAboveCenter(): boolean {
      return this.yPosition < this.yMidpoint
    },
    styling(): Object {
      const containerElement = this.$refs.container as HTMLDivElement | null
      const style: any = {
        top: this.xPosition,
        left: this.yPosition,
      }
      if (containerElement) {
        // position context menu to expand towards center screen
        // based on container element position
        //    _____________________________
        //   |              |              |
        //   |  x _____     |     _____ x  |
        //   |   |     |    |    |     |   |
        //   |   |     |    |    |     |   |
        //   |   |_____|    |    |_____|   |
        //   |              |              |
        //   |______________|______________|
        //   |              |              |
        //   |    _____     |    _____     |
        //   |   |     |    |   |     |    |
        //   |   |     |    |   |     |    |
        //   |   |_____|    |   |_____|    |
        //   |  x           |          x   |
        //   |______________|______________|
        if (this.isLeftOfCenter) {
          style.left = `${this.xPosition}px`
        } else {
          style.left = `${
            this.xPosition - containerElement.getBoundingClientRect().width
          }px`
        }

        if (this.isAboveCenter) {
          style.top = `${this.yPosition}px`
        } else {
          style.top = `${
            this.yPosition - containerElement.getBoundingClientRect().height
          }px`
        }
      }

      return style
    },
  },
  props: {
    /**
     * should the context menu be dismissed when the user
     * clicks on something inside the menu?
     */
    dismissOnInsideClick: { type: Boolean, default: true },
    /**
     * should the context menu be dismissed when the user
     * clicks on something outside the menu?
     * this will trigger a 'cancel' event if true.
     */
    dismissOnOutsideClick: { type: Boolean, default: true },
  },
  data() {
    return {
      // state
      isOpen: false,
      // position info
      innerWindowWidth: 0,
      xPosition: 0,
      yPosition: 0,
      xMidpoint: 0,
      yMidpoint: 0,
    }
  },
  methods: {
    /**
     * opens the context menu. This is typically done by grabbing the component via ref.
     * @param event the mouse event from the click, used in determining where to place
     * the context menu.
     */
    open(event: PointerEvent | undefined) {
      if (event) {
        // position the context menu
        this.setPositionFromEvent(event)

        // stop this event so it doesn't immediately close on the clickEventListener.
        event.stopPropagation()
      }

      // show context menu
      this.isOpen = true

      // add click event handler to dismiss context menu
      document.addEventListener('click', this.clickEventListener)
    },
    /**
     * Closes the context menu.
     */
    close(): void {
      document.removeEventListener('click', this.clickEventListener)
      this.isOpen = false
    },
    /**
     * Finds the width of the inner window to determine which direction to expand
     * the context menu.
     */
    getInnerWindowWidth(): void {
      // This is a fudge number.
      const EXCESS: number = 0.08333

      this.innerWindowWidth =
        document.documentElement.clientWidth -
        document.documentElement.clientWidth * EXCESS

      this.xMidpoint = window.innerWidth / 2
      this.yMidpoint = window.innerHeight / 2
    },
    setPositionFromEvent(event: PointerEvent): void {
      this.xPosition = event.clientX
      this.yPosition = event.clientY
    },
    /**
     * Handles the click event. Closes the menu for dismissOnInsideClick
     * and dismissOnOutsideEvent conditions.
     * @param event
     */
    clickEventListener(event: MouseEvent) {
      // check if we clicked inside the context menu or not
      const menu = this.$el
      let clickedInside = false
      if (event.target) {
        clickedInside = menu.contains(event.target as Node)
      }

      if (clickedInside && this.dismissOnInsideClick) {
        this.close()
        return
      }
      if (!clickedInside && this.dismissOnOutsideClick) {
        this.$emit('cancel')
        this.close()
        return
      }
    },
  },
  mounted() {
    this.$nextTick(function () {
      window.addEventListener('resize', this.getInnerWindowWidth)
      this.getInnerWindowWidth()
    })
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.getInnerWindowWidth)
    this.close()
  },
}
</script>

<style scoped>
.fixed {
  position: fixed;
}
.invisible {
  visibility: hidden;
}
.z-index {
  z-index: 100;
}
</style>