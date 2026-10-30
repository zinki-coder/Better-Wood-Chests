package betterwoodchests.modid;

import net.fabricmc.api.ModInitializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BetterWoodChests implements ModInitializer {
    public static final String MOD_ID = "better-wood-chests";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitialize() {
        LOGGER.info("Better Wood Chests loaded");
    }
}
