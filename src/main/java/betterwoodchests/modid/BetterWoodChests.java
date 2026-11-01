package betterwoodchests.modid;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.creativetab.v1.CreativeModeTabEvents;
import net.minecraft.world.item.CreativeModeTabs;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BetterWoodChests implements ModInitializer {
    public static final String MOD_ID = "better-wood-chests";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitialize() {
        ModBlocks.init();
        ModBlockEntities.init();
        CreativeModeTabEvents.modifyOutputEvent(CreativeModeTabs.FUNCTIONAL_BLOCKS)
            .register(entries -> ModBlocks.CHEST_ITEMS.values().forEach(entries::accept));
        LOGGER.info("Better Wood Chests loaded");
    }
}
